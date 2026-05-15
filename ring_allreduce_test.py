import torch
import torch.distributed as dist
import torch.multiprocessing as mp
import os

def ring_allreduce(tensor, rank, world_size):
    assert tensor.numel() % world_size == 0
    chunk_size = tensor.numel() // world_size
    chunks = list(tensor.view(world_size, chunk_size).unbind(dim=0))
    chunks = [c.contiguous().clone() for c in chunks]

    left = (rank - 1) % world_size
    right = (rank + 1) % world_size
    send_buf = torch.zeros(chunk_size, device=tensor.device)
    recv_buf = torch.zeros(chunk_size, device=tensor.device)

    # Phase 1: Reduce-Scatter
    for step in range(world_size - 1):
        send_idx = (rank - step) % world_size
        recv_idx = (rank - step - 1) % world_size

        send_buf.copy_(chunks[send_idx])
        req_s = dist.isend(send_buf, dst=right)
        req_r = dist.irecv(recv_buf, src=left)
        req_s.wait()
        req_r.wait()

        chunks[recv_idx] += recv_buf

    # Phase 2: AllGather
    for step in range(world_size - 1):
        send_idx = (rank - step + 1) % world_size
        recv_idx = (rank - step) % world_size

        send_buf.copy_(chunks[send_idx])
        req_s = dist.isend(send_buf, dst=right)
        req_r = dist.irecv(recv_buf, src=left)
        req_s.wait()
        req_r.wait()

        chunks[recv_idx].copy_(recv_buf)

    return torch.cat(chunks, dim=0)

def worker(rank, world_size):
    os.environ['MASTER_ADDR'] = 'localhost'
    os.environ['MASTER_PORT'] = '29500'
    dist.init_process_group('gloo', rank=rank, world_size=world_size)

    torch.manual_seed(rank)
    tensor = torch.randn(16)

    result_ring = ring_allreduce(tensor.clone(), rank, world_size)

    result_ref = tensor.clone()
    dist.all_reduce(result_ref, op=dist.ReduceOp.SUM)

    assert torch.allclose(result_ring, result_ref, atol=1e-5)
    print(f"Rank {rank}: PASSED!")
    dist.destroy_process_group()

if __name__ == '__main__':
    mp.spawn(worker, args=(4,), nprocs=4)
