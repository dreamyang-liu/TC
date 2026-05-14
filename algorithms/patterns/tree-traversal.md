# 二叉树递归 / 遍历模板（易记版）

## 本质一句话
> **树 = 根 + 左子树 + 右子树。递归函数只想清楚：当前节点要做什么，子树返回什么。**

## 三种遍历（顺序就一个字差别）

```python
def preorder(root):    # 根 → 左 → 右
    if not root: return
    visit(root)
    preorder(root.left)
    preorder(root.right)

def inorder(root):     # 左 → 根 → 右（BST 升序）
    if not root: return
    inorder(root.left)
    visit(root)
    inorder(root.right)

def postorder(root):   # 左 → 右 → 根（释放、聚合子树信息）
    if not root: return
    postorder(root.left)
    postorder(root.right)
    visit(root)
```

**何时用哪种**：
- **前序**：自顶向下传递信息（路径、深度）
- **中序**：BST 特性（中序 = 升序）
- **后序**：自底向上聚合信息（子树和、高度、是否平衡）

## 递归三问（解任何树题）

1. **这个函数返回什么？**（设计签名）
2. **递归基（叶子 / 空）返回什么？**
3. **当前节点怎么用左右子树的返回值组合答案？**

### 例：树的最大深度（后序）

```python
def max_depth(root):
    if not root: return 0                            # 1. 函数返回深度
    return 1 + max(max_depth(root.left),             # 2. 空树深度 0
                   max_depth(root.right))            # 3. 当前 = 1 + 子树最大
```

### 例：树的直径（后序，两个返回值的诀窍）

```python
def diameter(root):
    ans = 0
    def depth(node):
        nonlocal ans
        if not node: return 0
        L = depth(node.left)
        R = depth(node.right)
        ans = max(ans, L + R)        # 经过 node 的最长路径
        return 1 + max(L, R)         # 返回给父节点的"深度"
    depth(root)
    return ans
```

**口诀**：**"经过我的"** 在内部更新答案；**"返回给上面用的"** 是函数返回值 —— 两者不同！

## 迭代遍历（用栈）

```python
def inorder_iter(root):
    stack, ans = [], []
    cur = root
    while cur or stack:
        while cur:
            stack.append(cur)
            cur = cur.left
        cur = stack.pop()
        ans.append(cur.val)
        cur = cur.right
    return ans
```

## Morris 遍历（O(1) 空间，进阶）

利用叶子节点空闲的 right 指针指回中序前驱，遍历完再恢复。只在面试要求 O(1) 空间时用。

## 层序遍历（BFS）

见 [BFS 模板](bfs.md)。

## 怎么不写错
- **base case 永远在最前面**：`if not root: return ...`
- **递归函数返回值**和**外部累积答案**要区分清楚
- BST 想找第 K 小 / 验证有效性 → **走中序**
- 子树聚合信息 → **走后序**
- 路径类问题（路径和、最长路径）→ **后序 + 两个量**（经过我的 vs 给父亲用的）

## 热身题
- [104. 二叉树的最大深度](https://leetcode.cn/problems/maximum-depth-of-binary-tree/)
- [226. 翻转二叉树](https://leetcode.cn/problems/invert-binary-tree/)
- [101. 对称二叉树](https://leetcode.cn/problems/symmetric-tree/)
- [98. 验证二叉搜索树](https://leetcode.cn/problems/validate-binary-search-tree/)
- [110. 平衡二叉树](https://leetcode.cn/problems/balanced-binary-tree/)

## 进阶题
- [543. 二叉树的直径](https://leetcode.cn/problems/diameter-of-binary-tree/)
- [124. 二叉树中的最大路径和](https://leetcode.cn/problems/binary-tree-maximum-path-sum/)
- [236. 二叉树的最近公共祖先](https://leetcode.cn/problems/lowest-common-ancestor-of-a-binary-tree/)
- [105. 从前序与中序遍历序列构造二叉树](https://leetcode.cn/problems/construct-binary-tree-from-preorder-and-inorder-traversal/)
- [297. 二叉树的序列化与反序列化](https://leetcode.cn/problems/serialize-and-deserialize-binary-tree/)
- [437. 路径总和 III](https://leetcode.cn/problems/path-sum-iii/)（前缀和 + DFS）
