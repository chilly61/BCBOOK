import hashlib
import time
import random


class Blockchain:
    def __init__(self):
        """
        初始化区块链类，设置创世区块和必要的链上数据结构
        """
        self.chain = []  # 用于存储所有区块的链
        self.current_transactions = []  # 当前等待写入区块的交易
        self.nodes = {}  # 记录所有节点信息 {node_id: node_info}
        self.DIDs = {}  # 记录所有 DID 信息 {did: node_id}
        self.rewards = {}  # 记录节点的奖励 {node_id: reward_amount}

        # 创世区块
        self.new_block(previous_hash='1', proof=100, current_hash='00')

    def new_block(self, proof, previous_hash=None, current_hash=None):
        """
        创建一个新块并将其加入到区块链中
        :param proof: 工作量证明算法给出的证明
        :param previous_hash: 前一个区块的哈希
        :return: 新区块
        """
        block = {
            'index': len(self.chain) + 1,
            'timestamp': time.time(),
            'transactions': self.current_transactions,
            'proof': proof,
            'previous_hash': previous_hash or self.hash(self.chain[-1]),
            
        }
        current_hash = self.hash(block)
       
        # 重置当前的交易记录
        self.current_transactions = []
        self.chain.append(block)
        return block

    @staticmethod
    def hash(block):
        """
        生成块的 SHA-256 哈希值
        :param block: 区块
        :return: 区块的哈希值
        """
        block_string = str(block).encode()
        return hashlib.sha256(block_string).hexdigest()

    def new_transaction(self, sender, recipient, amount, transaction_type, extra_data=None):
        """
        创建一个新的交易加入到下一个待挖的区块中
        :param sender: 发送者的地址或 DID
        :param recipient: 接收者的地址或 DID
        :param amount: 交易的金额
        :param transaction_type: 交易类型（如：资金交易、身份验证等）
        :param extra_data: 额外数据，用于存储与交易相关的加密信息等
        :return: 包含此交易的区块的索引
        """
        transaction = {
            'sender': sender,
            'recipient': recipient,
            'amount': amount,
            'transaction_type': transaction_type,
            'extra_data': extra_data,
        }

        self.current_transactions.append(transaction)
        return self.last_block['index'] + 1

    @property
    def last_block(self):
        return self.chain[-1]

    def register_node(self, node_id, tax, contribution, public_key):
        """
        注册新节点并记录节点的相关信息
        :param node_id: 节点 ID
        :param tax: 节点的税务信息
        :param contribution: 节点的社会贡献值
        :param public_key: 节点的公钥
        """
        self.nodes[node_id] = {
            'tax': tax,
            'contribution': contribution,
            'public_key': public_key,
        }

    def register_DID(self, did, node_id):
        """
        为某个节点注册 DID 并将其与节点关联
        :param did: DID 标识
        :param node_id: 关联的节点 ID
        """
        self.DIDs[did] = node_id

    def verify_DID(self, did, public_key):
        """
        验证某个 DID 是否匹配给定的公钥
        :param did: 需要验证的 DID
        :param public_key: 节点的公钥
        :return: 验证结果 True or False
        """
        node_id = self.DIDs.get(did)
        if node_id:
            node_info = self.nodes.get(node_id)
            if node_info and node_info['public_key'] == public_key:
                return True
        return False

    def record_government_action(self, did, department, action_type, encrypted_message):
        """
        记录政府部门的行动，如调查、协作等
        :param did: 涉及的 DID
        :param department: 执行操作的部门
        :param action_type: 操作类型（如：调查、处罚等）
        :param encrypted_message: 加密的行动细节
        :return: 包含此政府行动的区块的索引
        """
        action = {
            'did': did,
            'department': department,
            'action_type': action_type,
            'encrypted_message': encrypted_message,
        }

        self.current_transactions.append(action)
        return self.last_block['index'] + 1

    def resolve_conflict(self, did, involved_departments):
        """
        记录多部门协作来解决某个 DID 的纠纷或违规行为
        :param did: 涉及的 DID
        :param involved_departments: 参与协作的部门列表
        """
        conflict_record = {
            'did': did,
            'involved_departments': involved_departments,
            'action': 'resolve_conflict',
        }
        self.current_transactions.append(conflict_record)
        return self.last_block['index'] + 1

    def proof_of_contribution(self, node_id):
        """
        用于选择区块生产者的 PoCC（Proof of Civil Contribution）算法
        :param node_id: 节点 ID
        :return: 是否选中为矿工
        """
        node_info = self.nodes.get(node_id)
        if not node_info:
            return False

        # 基于贡献值和税务信息的概率性选择矿工
        contribution = node_info['contribution']
        selection_probability = random.uniform(0, 1)

        # 简化版贡献选择机制：贡献值越大，选择为矿工的概率越高
        return selection_probability < contribution

    def reward_block(self, node_id):
        """
        根据贡献值奖励矿工
        :param node_id: 当前生产区块的矿工节点
        """
        if node_id in self.nodes:
            reward = self.nodes[node_id]['contribution'] * 0.01  # 假设奖励是贡献值的 1%
            if node_id in self.rewards:
                self.rewards[node_id] += reward
            else:
                self.rewards[node_id] = reward

    def validate_block(self, block):
        """
        验证区块是否合法，检查区块哈希与工作量证明
        :param block: 区块
        :return: 验证结果 True or False
        """
        # 验证哈希是否匹配
        block_hash = self.hash(block)
        if block['previous_hash'] != self.chain[-1]['previous_hash']:
            return False
        # 验证工作量证明，其他验证机制可进一步扩展
        return block_hash.startswith('0000')  # 假设简单的前四个字符为零的证明机制

    # 还没有结束！！！


blockchain = Blockchain()
newproof = 12345
previous_hash = blockchain.hash(
    blockchain.chain[-1]) if blockchain.chain else None
blockchain.current_transactions = ["ALICE", "BOB"]
new_block = blockchain.new_block(newproof, previous_hash)
