**Preface test**:
You can see basic structure of the blocks and their contents.
![QQ_1726007674482](https://github.com/user-attachments/assets/90d4e44c-efa7-4531-8a74-a3a32142de4f)

**Instance illustration:**

**Step 1:**
Alice creates a personal node, which is not trusted by anyone. She encrypted the privacy and sent it to the rootnode:BCBOOK.
BCBOOK checked the privacy and recorded it offline, which is not recorded on blockchain.
BCBOOK generated the DID for Alice based on the privacy she sent and her public key.
The blockchain recorded the process of the interaction between node alice and rootnode. Meanwhile, it updated the nodes and dids in the chain.

In this step, you can see how we simulate:
1. register a new node on chain
2. apply a new did from node alice
3. reply and register a new did for a node from rootnode


![QQ_1726003333967](https://github.com/user-attachments/assets/2167ca29-6fb4-4c34-9c5d-127c021aaef9)
![QQ_1726003374950](https://github.com/user-attachments/assets/b10368ae-0aad-4708-9b7e-37ac1f3236b9)
Nodes and DIDs update
![QQ_1726003433453](https://github.com/user-attachments/assets/ab57d88c-af2a-4709-ae6a-7eb1dbf66098)

**Step 2:**
Alice then uses her DID to apply the admission to UBC Engineering. After 4 years' studying, she finally graduated from the UBC.

In this step, you can see:
1. How to encrypt the info between nodes.
   
![QQ_1726006790222](https://github.com/user-attachments/assets/1a25eb93-48b8-4ff4-b33c-2a57ed6fd3b4)

2. How to append and remove dids in a node .
![QQ_1726006890833](https://github.com/user-attachments/assets/4dc7e2bc-6338-4886-872b-080f6b7b7e7b)

3. How to make a civil activity with multi-nodes.
