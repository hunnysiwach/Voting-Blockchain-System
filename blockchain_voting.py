import hashlib
import time
import json

class Voter:
    def _init_(self, voter_id, name):
        self.voter_id = voter_id
        self.name = name
        self.has_voted = False

    def to_dict(self):
        return {'voter_id': self.voter_id, 'name': self.name, 'has_voted': self.has_voted}

class Candidate:
    def _init_(self, candidate_id, name):
        self.candidate_id = candidate_id
        self.name = name

    def to_dict(self):
        return {'candidate_id': self.candidate_id, 'name': self.name}

class Transaction:
    def _init_(self, voter_id, candidate_id):
        self.voter_id = voter_id
        self.candidate_id = candidate_id
        self.timestamp = time.time()

    def to_dict(self):
        return {
            'voter_id': self.voter_id,
            'candidate_id': self.candidate_id,
            'timestamp': self.timestamp
        }

    def _str_(self):
        return f"Voter {self.voter_id} voted for Candidate {self.candidate_id} at {time.ctime(self.timestamp)}"

class Block:
    def _init_(self, index, transactions, timestamp, previous_hash):
        self.index = index
        self.transactions = transactions
        self.timestamp = timestamp
        self.previous_hash = previous_hash
        self.nonce = 0
        self.hash = self.calculate_hash()

    def calculate_hash(self):
        block_string = json.dumps({
            "index": self.index,
            "transactions": [t.to_dict() for t in self.transactions],
            "timestamp": self.timestamp,
            "previous_hash": self.previous_hash,
            "nonce": self.nonce
        }, sort_keys=True).encode()
        return hashlib.sha256(block_string).hexdigest()

class Blockchain:
    def _init_(self):
        self.chain = []
        self.pending_transactions = []
        self.voters = {}
        self.candidates = {}
        self.create_genesis_block()

    def create_genesis_block(self):
        self.chain.append(
            Block(0, [], time.time(), "0")
        )

    @property
    def last_block(self):
        return self.chain[-1]

    def add_transaction(self, transaction):
        self.pending_transactions.append(transaction)

    def mine_pending_transactions(self):
        if not self.pending_transactions:
            print("\n❌ No pending votes to add to a block.")
            return

        new_block = Block(
            len(self.chain),
            self.pending_transactions,
            time.time(),
            self.last_block.hash
        )
        
        self.chain.append(new_block)
        self.pending_transactions = []
        print(f"\n✅ Block #{new_block.index} successfully added to the chain!")
        print(f"   Hash: {new_block.hash}")

    def add_voter(self, voter_id, name):
        if voter_id in self.voters:
            print(f"\n❌ Input validation failed: Voter ID '{voter_id}' already exists.")
            return False
        self.voters[voter_id] = Voter(voter_id, name)
        print(f"\n✅ Voter '{name}' ({voter_id}) registered successfully.")
        return True

    def add_candidate(self, candidate_id, name):
        if candidate_id in self.candidates:
            print(f"\n❌ Input validation failed: Candidate ID '{candidate_id}' already exists.")
            return False
        self.candidates[candidate_id] = Candidate(candidate_id, name)
        print(f"\n✅ Candidate '{name}' ({candidate_id}) registered successfully.")
        return True

    def cast_vote(self, voter_id, candidate_id):
        if voter_id not in self.voters:
            print(f"\n❌ Voting failed: Voter ID '{voter_id}' not found.")
            return False

        voter = self.voters[voter_id]

        if voter.has_voted:
            print(f"\n❌ Voting failed: Voter '{voter.name}' ({voter_id}) has already voted.")
            return False

        if candidate_id not in self.candidates:
            print(f"\n❌ Voting failed: Candidate ID '{candidate_id}' not found.")
            return False

        vote_transaction = Transaction(voter_id, candidate_id)
        self.add_transaction(vote_transaction)
        
        self.mine_pending_transactions() 
        
        voter.has_voted = True
        print(f"   Voter '{voter.name}' has been marked as voted.")
        return True

    def is_chain_valid(self):
        for i in range(1, len(self.chain)):
            current_block = self.chain[i]
            previous_block = self.chain[i-1]

            if current_block.hash != current_block.calculate_hash():
                print(f"Chain Validation FAILED at Block #{current_block.index}: Hash Mismatch")
                print(f"   Calculated: {current_block.calculate_hash()}")
                print(f"   Stored: {current_block.hash}")
                return False

            if current_block.previous_hash != previous_block.hash:
                print(f"Chain Validation FAILED at Block #{current_block.index}: Previous Hash Mismatch")
                print(f"   Expected Previous Hash: {previous_block.hash}")
                print(f"   Stored Previous Hash: {current_block.previous_hash}")
                return False
        
        return True

    def print_chain_contents(self):
        if len(self.chain) <= 1:
            print("\nThe blockchain only contains the Genesis Block.")
            return

        for block in self.chain:
            print("-" * 40)
            print(f"Block Index:    {block.index}")
            print(f"Timestamp:      {time.ctime(block.timestamp)}")
            print(f"Hash:           {block.hash}")
            print(f"Previous Hash:  {block.previous_hash}")
            print("Transactions:")
            if block.transactions:
                for tx in block.transactions:
                    print(f"  - {tx}")
            else:
                print("  - [No transactions (Genesis Block)]")

def display_menu():
    print("\n" + "=" * 40)
    print("🗳  Voting Management System on Blockchain")
    print("=" * 40)
    print("1. Add Candidate (Admin)")
    print("2. Add Voter (Admin)")