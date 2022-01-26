import sqlite3
import account
import random
import datetime

choice = "-"

db = sqlite3.connect("bank1234.sqlite")
db.execute("CREATE TABLE IF NOT EXISTS accounts (_id Integer primary key, name text, email text, phone text, "
           "balance integer, hashed_pwd, text);")
db.execute("CREATE TABLE IF NOT EXISTS transactions (timestamp text primary key, debit_id Integer, "
           "credit_id Integer, amount Integer, status text, message text);")


def create_account():
	ac = account.Account()
	q1 = f"INSERT INTO accounts (_id, name, email, phone, balance, hashed_pwd) VALUES({ac.account_no}, '{ac.name}', '{ac.email}', '{ac.phone}', {ac.balance}, '{ac.hashed_pwd}')"
	# q2 = f"INSERT INTO transactions (_id, operation, status, timestamp, message) VALUES({ac.account_no}, '1', '1', {ac.account_no[:-4]}, 'Opening Balance Transaction')"
	cursor = db.cursor()
	cursor.execute(q1)
	# cursor.execute(q2)
	cursor.connection.commit()
	cursor.close()


def list_accounts():
	query = "SELECT _id, name, email from accounts"
	cursor = db.cursor()
	print("Please find all the accounts: ")
	cursor.execute(query)
	for acc_no, acc_name, acc_email in cursor:
		print(f"{acc_no}:{acc_name}:{acc_email}")
	cursor.close()


def account_present(acc_no):
	query = f"SELECT count(_id) from accounts where _id = {acc_no}"
	cursor = db.cursor()
	cursor.execute(query)
	c = cursor.fetchone()[0]
	cursor.close()
	print(c)
	print(type(c))
	return c == 1


def debitable(acc_no, amt):
	query = f"SELECT _id, balance from accounts where _id = {acc_no}"
	cursor = db.cursor()
	cursor.execute(query)
	available_balance = cursor.fetchone()[1]
	return available_balance >= amt


def do_transaction(debit_acc, amt, credit_acc):
	# Update the balance of debitor and creditor in the contacts table
	cursor = db.cursor()
	cursor.execute(f"select name, balance from accounts where _id = {int(debit_acc)}")
	(debitor_name, debitor_balance) = cursor.fetchone()
	debitor_balance -= amt
	cursor.execute(f"select name, balance from accounts where _id = {int(credit_acc)}")
	(creditor_name, creditor_balance) = cursor.fetchone()
	creditor_balance += amt
	cursor.execute(f"update accounts set balance = {debitor_balance} where _id = {debit_acc}")
	cursor.execute(f"update accounts set balance = {creditor_balance} where _id = {credit_acc}")
	print(f"Transfer of {amt} successful from {debitor_name} to {creditor_name}")
	print(f"{debitor_name}'s balance = {debitor_balance}")
	print(f"{creditor_name}'s balance = {creditor_balance}")


def update_trans_table(debit_acc, amt, credit_acc, status_code, msg_code):
	dt = datetime.datetime.utcnow()
	yy = str(dt.year % 100)
	mm = str(dt.month) if dt.month > 9 else "0" + str(dt.month)
	dd = str(dt.day) if dt.day > 9 else "0" + str(dt.day)
	hh = str(dt.hour) if dt.hour > 9 else "0" + str(dt.hour)
	minn = str(dt.minute) if dt.minute > 9 else "0" + str(dt.minute)
	ss = str(dt.second) if dt.second > 9 else "0" + str(dt.second)
	timestamp = yy + mm + dd + hh + minn + ss
	stat = {0: "Failure", 1: "Success"}
	msg = {-1: "Insufficient balance.", 0: "Connectivity issues.", 1: "Success"}
	cursor = db.cursor()
	cursor.execute(f"INSERT INTO transactions VALUES('{timestamp}', {debit_acc}, {credit_acc},"
	               f" {amt}, '{stat[status_code]}', '{msg[msg_code]}')")
	cursor.connection.commit()
	cursor.close()


def pwd_verified(acc_no):
	cursor = db.cursor()
	cursor.execute(f"select hashed_pwd from accounts where _id = {acc_no}")
	hp = cursor.fetchone()[0]
	# print("Retrived Hash of the password = " + hp)
	# print("Type of the retrived hashed password: " + str(type(hp)))
	ps1 = input("Enter password for the corresponding account: ")
	# print("Hash of the typed password: " + ps1)
	# print("Type of the typed Hash password: " + str(type(ps1)))

	return ps1 == hp
	# cursor.execute(f"Delete from accounts where _id = {acc_no}")


def transact():
	list_accounts()
	debit_from_acc = int(input("Enter the account Number you want to withdraw money from: "))
	debit_amount = int(input("Enter the amount you want to withdraw: "))
	credit_to_acc = int(input("Enter the destination account you want to deposit the amount: "))
	if account_present(debit_from_acc):
		if debitable(debit_from_acc, debit_amount):
			print("Initiating Transaction: ")
			if random.randint(1, 3) != 3:
				do_transaction(debit_from_acc, debit_amount, credit_to_acc)
				# this updates the contacts table
				update_trans_table(debit_from_acc, debit_amount, credit_to_acc, 1, 1)
				# this updates the transaction table
			else:
				print("Transaction Failed due to Network/Connectivity issues.")
				update_trans_table(debit_from_acc, debit_amount, credit_to_acc, 0, 0)
		else:
			print("Transaction could not be completed due to insufficient balance.")
			update_trans_table(debit_from_acc, debit_amount, credit_to_acc, 0, -1)
	else:
		print("Failure: Invalid Account")


def delete_account():
	list_accounts()
	del_acc_no = int(input("Enter the account Number you want to delete: "))
	if account_present(del_acc_no):
		print("Please verify the password: ")
		if pwd_verified(del_acc_no):
			query = f"DELETE FROM accounts where _id = {del_acc_no}"
			cursor = db.cursor()
			cursor.execute(query)
			cursor.connection.commit()
			cursor.close()
			print("Account : " + str(del_acc_no) + " has been deleted")
		else:
			print("Password could not be verified. Transaction Cancelled...")
	else:
		print("Account does not exist.")


def balance_enquiry():
	list_accounts()
	acc_no = int(input("Enter your account number: "))
	if account_present(acc_no):
		if pwd_verified(acc_no):
			cursor = db.cursor()
			cursor.execute(f"select name, balance from accounts where _id = {acc_no}")

			(nam, bal) = cursor.fetchone()
			cursor.close()
			print(f"Hello {nam}, your current balance is: {bal}")
		else:
			print("Password Could not be verified. Transaction Cancelled")
	else:
		print("Invalid Account")


def show_all_transactions():
	list_accounts()
	acc_no = int(input("Enter your account number: "))
	if account_present(acc_no):
		if pwd_verified(acc_no):
			cursor = db.cursor()
			cursor.execute(f"select * from transactions where credit_id = {acc_no} or debit_id = {acc_no}")
			print("TimeStamp:\t\tD/W\t\t\tAmount\tStatus\tMessage")
			for record in cursor:
				dw = "Deposit " if record[2] == acc_no else "Withdraw"
				print(f"{record[0]}\t{dw}\t{record[3]}\t{record[4]}\t{record[5]}")
			cursor.execute(f"select balance from accounts where _id = {acc_no}")
			final_balance = cursor.fetchone()[0]
			print(f"Final balance = {final_balance}")
			cursor.close()
		else:
			print("Password could not be verified")
	else:
		print("Account does not exist")


while choice != "7":
	if choice not in "12345":
		print("1: Create a New Account")
		print("2: List all accounts present currently")
		print("3: Do a transaction")
		print("4: Balance Enquiry")
		print("5: Show all Transactions for an user.")
		print("6: Delete an existing account")
		print("7: Exit")
	else:
		if choice == "1":
			create_account()
		elif choice == "2":
			list_accounts()
		elif choice == "3":
			transact()
		elif choice == "4":
			balance_enquiry()
		elif choice == "5":
			show_all_transactions()
		elif choice == "6":
			delete_account()
	choice = input()

db.commit()
db.close()
