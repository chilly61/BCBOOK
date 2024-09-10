import base64
import hashlib
import time
import random
from cryptography.hazmat.primitives.asymmetric import rsa
from cryptography.hazmat.primitives import serialization
import encryption


class Node:
    def __init__(self, title, address, node_type, owners):
        '''
        "初始化节点"
        '''
        self.title = title  # 节点名称
        self.address = address  # 节点的public key作为地址公开
        self.type = node_type  # 节点类型，包括personal，business和government
        self.affiliated_nodes = []  # 附属节点列表
        self.didslist = []  # 节点的附属DIDs列表
        self.owners = owners  # 节点的所有者DIDs
        self.contributions = 0  # 节点当前的贡献值，基于Owner的合计贡献值
        self.functions = []  # 节点规定的服务内容或权限，各节点不同

    def __repr__(self):
        return (f"Node(title={self.title}, address={self.address}, type={self.type}, "
                f"didslist={self.didslist}, owners={self.owners}, contributions={self.contributions}, "
                f"functions={self.functions}, affiliated_nodes={self.affiliated_nodes})")


class DID:
    def __init__(self, did_id, civilcontribution, issuer_address, node_address, rootnode_address, rootnode_did_list):
        """
        初始化DID
        :param civilcontribution: 申请者的社会贡献值
        :param issuer_address: 发行者的地址,必须是BCBOOK或BCBOOK owner_DID
        :param node_address: 申请DID的个人节点地址(即public key)
        """
        self.did_id = did_id
        self.civilcontribution = civilcontribution  # 社会贡献值
        self.cc_history = civilcontribution  # 贡献值历史记录（初始为申请时的贡献值）
        self.current_cc = 0  # 当前贡献值
        self.issuer = issuer_address  # DID的发行者地址，验证时需为BCBOOK或BCBOOK owner_DID
        self.node_address = node_address  # 申请DID的节点地址（作为身份标识）
        self.is_valid = self.validate_issuer(
            rootnode_address, rootnode_did_list)  # 验证DID是否由合法发行者发出

    def validate_issuer(self, rootnode_address, rootnode_did_list):
        """
        验证DID的发行者是否为BCBOOK或BCBOOK的owner_DID
        :return: 返回True如果发行者有效,否则False
        """
        # 假设 BCBOOK_ADDRESS 是系统内的BCBOOK节点的地址
        BCBOOK_ADDRESS = rootnode_address
        owner_did_list = rootnode_did_list  # BCBOOK的owner_DID列表

        if self.issuer == BCBOOK_ADDRESS or self.issuer in owner_did_list:
            return True
        return False


class Blockchain:
    def __init__(self, rootnode):
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
        # 根节点 BCBOOK

        self.register_node(rootnode)

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
        """
        transaction = {
            'sender': sender,  # 发送者的地址或 DID
            'recipient': recipient,  # 接收者的地址或 DID
            'amount': amount,  # 交易的金额
            'transaction_type': transaction_type,  # 交易类型（如：资金交易、身份验证等）
            'extra_data': extra_data,  # 额外数据，用于存储与交易相关的加密信息等
            'timestamp': time.time()  # 记录交易时间
        }

        self.current_transactions.append(transaction)
        return self.last_block['index'] + 1  # 包含此交易的区块的索引

    @property
    def last_block(self):
        return self.chain[-1]

    def register_node(self, node):
        """
        注册新节点并记录节点的相关信息
        :param node_id: 节点 ID
        :param tax: 节点的税务信息
        :param contribution: 节点的社会贡献值
        :param public_key: 节点的公钥
        """
        if node.address not in self.nodes:
            self.nodes[node.address] = node
            self.new_transaction(
                sender=node.address,
                recipient=node.address,
                amount=0,  # 不涉及资金转账
                transaction_type="register",
                extra_data=f"Node {node.address} is now registered in the blockchain."
            )
        else:
            raise ValueError("节点已经存在！")

    def create_affiliated_node(self, parent_node_address, new_node):
        """
        创建并注册一个附属节点，并记录为一笔交易
        :param parent_node_address: 父节点地址
        :param new_node: 新的附属节点
        """
        # 验证父节点是否存在
        if parent_node_address in self.nodes:
            # 注册新节点
            self.register_node(new_node)

            # 更新父节点的附属节点列表
            self.nodes[parent_node_address].affiliated_nodes.append(
                new_node.address)

            # 创建一笔附属节点交易，并记录附属关系
            self.new_transaction(
                sender=parent_node_address,
                recipient=new_node.address,
                amount=0,  # 不涉及资金转账
                transaction_type="affiliation",
                extra_data=f"Node {new_node.address} is now an affiliated node of {parent_node_address}."
            )
        else:
            raise ValueError("父节点不存在！")

    def apply_DID(self, Apply_Node, rootnode, hash_privacy):
        """
        某节点向BCBOOK申请一个DID
        """
        self.new_transaction(
            sender=Apply_Node,
            recipient=rootnode.address,
            amount=0,  # 不涉及资金转账
            transaction_type="register",
            extra_data=f"Node {Apply_Node.address} is now an applying for a DID. The privacy info is encrypted as {hash_privacy}"
        )

    def register_DID(self, DID):
        """
        为某个节点注册 DID 并将其与节点关联
        :param did: DID 标识
        :param node_id: 关联的节点 ID
        """
        self.DIDs[DID.did_id] = DID
        self.new_transaction(
            sender=DID.issuer,
            recipient=DID.node_address,
            amount=0,  # 不涉及资金转账
            transaction_type="register",
            extra_data=f"Node:{DID.node_address} is the owner of DID:{DID.did_id}, verified by Node: {DID.issuer}."
        )

    def proof_of_contribution(self, node_id):
        """
        用于选择区块生产者的 PoCC(Proof of Civil Contribution)算法
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
            reward = self.nodes[node_id].contributions * \
                0.01  # 假设奖励是贡献值的 1%
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


def generate_key_pair():
    """
    生成公钥和私钥
    :return: (private_key, public_key)
    """
    # 生成私钥
    private_key = rsa.generate_private_key(
        public_exponent=65537,
        key_size=512,
    )

    # 生成公钥
    public_key = private_key.public_key()

    # 将私钥和公钥序列化为PEM格式
    private_pem = private_key.private_bytes(
        encoding=serialization.Encoding.PEM,
        format=serialization.PrivateFormat.PKCS8,
        encryption_algorithm=serialization.NoEncryption()
    )

    public_pem = public_key.public_bytes(
        encoding=serialization.Encoding.PEM,
        format=serialization.PublicFormat.SubjectPublicKeyInfo
    )

    return private_pem, public_pem


BCBOOK = Node("UBC", "BCBOOK", "business", ["Alice", "Bob"])
blockchain = Blockchain(rootnode=BCBOOK)

'''
# New block test

newproof = 12345
previous_hash = blockchain.hash(
    blockchain.chain[-1]) if blockchain.chain else None
blockchain.current_transactions = ["ALICE", "BOB"]
new_block = blockchain.new_block(newproof, previous_hash)


# Node Test
node_ubc = Node("UBC", "UBC001", "business", ["Alice", "Bob"])
blockchain.register_node(node_ubc)
affiliated_node = Node("UBC Affiliated Node A1", "address_UBC_A1",
                       "business", ["UBC_A1", "UBC_A2"])
blockchain.create_affiliated_node(node_ubc.address, affiliated_node)
print(blockchain.current_transactions)
print(blockchain.nodes[node_ubc.address])
previous_hash = blockchain.hash(
    blockchain.chain[-1]) if blockchain.chain else None
new_block = blockchain.new_block(newproof, previous_hash)
# DID Test
'''
# Instance
'''
Step 1: Alice applies for a did from BCBOOK
'''
BCBOOK = blockchain.nodes['BCBOOK']
public_bcbook, private_bcbook, public_key_bcbook, private_key_bcbook = encryption.generate_public_key_string()

# 使用Base64编码将公钥转换为字符串
public_alice, private_alice, public_key_alice, private_key_alice = encryption.generate_public_key_string()
node_alice = Node("Alice", public_alice, 'personal', '')
blockchain.register_node(node_alice)


personal_info = encryption.generate_personal_info(
    "John Doe", "john.doe@example.com", "1234567890", "123 Main St, Anytown, USA", "P1234567")
encrypted_info = encryption.encrypt_personal_info(
    personal_info, public_key_bcbook)
hash_value = encryption.calculate_hash(str(encrypted_info))
blockchain.apply_DID(Apply_Node=node_alice, rootnode=BCBOOK,
                     hash_privacy=hash_value)

decrypted_info = encryption.decrypt_personal_info(
    encrypted_info, private_key_bcbook)

alice_id = encryption.create_did(decrypted_info, public_alice)
Alice_DID = DID(did_id=alice_id, civilcontribution=100,
                issuer_address=BCBOOK.address, node_address=node_alice.address,
                rootnode_address=BCBOOK.address, rootnode_did_list=BCBOOK.didslist)
# blockchain.register_DID("approved",)


blockchain.register_DID(Alice_DID)
newproof = 12345
previous_hash = blockchain.hash(
    blockchain.chain[-1]) if blockchain.chain else None
new_block = blockchain.new_block(newproof, previous_hash)
blockchain.reward_block(node_alice.address)
'''
Step 2: Alice applies to join the UBC using the DID
'''
