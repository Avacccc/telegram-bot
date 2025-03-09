import asyncio
from client import run_client
from config import accounts


# Main function to run selected account
def main():
    print("Select the account to use:")
    for i, account in enumerate(accounts):
        print(f"{i + 1}. {account['session_name']}")
    account_id = int(input("Enter the number of the account: ")) - 1
    message_id = int(input("Enter the message id: "))

    if 0 <= account_id < len(accounts):
        selected_account = accounts[account_id]
        asyncio.run(run_client(selected_account, message_id))
    else:
        print("Invalid choice. Please try again.")
        main()

# Run the script
if __name__ == "__main__":
    main()