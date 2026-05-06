import sys
import os
sys.path.append(os.getcwd())
from database import update_warehouse_inventory, get_global_inventory

def test():
    invs = get_global_inventory()
    if invs:
        target_inv = invs[0]
        print(f"Targeting: {target_inv}")
        res = update_warehouse_inventory(target_inv['inventory_id'], int(target_inv['quantity_on_hand']) + 1)
        print("Update result:", res)
        invs_after = get_global_inventory()
        print(f"After: {invs_after[0]}")
    else:
        print("No inventory found")

if __name__ == '__main__':
    test()
