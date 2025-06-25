from add_account import add_account
from add_receipt import add_receipt
from add_payment import add_payment

def main():
    while True:
        print("\n--- BAHI-KHATA ---")
        print("1. Add New Account")
        print("2. Add Receipt (Money Received)")
        print("3. Add Payment (Money Paid)")
        print("4. Exit")
        choice = input("Choose an option: ")

        if choice == '1':
            add_account()
        elif choice == '2':
            add_receipt()
        elif choice == '3':
            add_payment()
        elif choice == '4':
            print("Exiting. Bye!")
            break
        else:
            print("Invalid choice. Please enter 1-4.")

if __name__ == "__main__":
    main()
