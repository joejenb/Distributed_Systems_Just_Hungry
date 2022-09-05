import Pyro4

def view_orders():
	global user_id
	if not user_id:
		print()
		print("			No orders to display")
	else:
		try:
			user, err = hungry_server.get_user(user_id)
			if type(err) == str:
				print(err)
			elif err:
				raise ValueError
		except:
			print("Cannot connect to server currently, please try again later")
			exit(1)
		try:
			user_orders, err = hungry_server.get_user_orders(user_id)
			if type(err) == str:
				print(err)
			elif err:
				raise ValueError
		except:
			print("Cannot connect to server currently, please try again later")
			exit(1)
		
		print()
		print("Name:	" + user["Name"] + "	Postcode:	" + user["Postcode"] + ":\n")
		for order in user_orders.keys():
			print("		Order Id: " + str(order) + "		Restaurant: " + user_orders[order]["restaurant"]["restaurant"] + "		Order: " + user_orders[order]["order"]["order"])



def place_order(res_id, item_id):
	global user_id
	if not user_id:
		user, invalid = {}, True

		while invalid:
			print()
			print("Please enter your name and postcode, or press enter to exit order:")
			user["name"] = input("		Name>	")

			if user["name"]:
				user["postcode"] = input("		Postcode>	")
				if user["postcode"]:

					try:
						user_id, err = hungry_server.add_user(user)
						if type(err) == str:
							print(err)
						elif err:
							raise ValueError
						else:
							invalid = False
					except:
						print("Cannot connect to server currently, please try again later")
						exit(1)

				else:
					return True
			else:
				return True
	try:
		order_id, err = hungry_server.order(user_id, res_id, item_id)
		if type(err) == str:
			print(err)
		elif err:
			raise ValueError
	except:
		print("Cannot connect to server currently, please try again later")
		exit(1)
	print()
	print("Success, your order has been placed. Order Id:	"+str(order_id))
	main()


def view_menu(res_id):
	go_back = False
	while not go_back:
		
		try:
			menu, err = hungry_server.get_menu(res_id)	
			if type(err) == str:
				print(err)
			elif err:
				raise ValueError
		except:
			print("Cannot connect to server currently, please try again later")
			exit(1)

		choice = make_choice("a dish", menu+["Go Back"])
		if choice == len(menu) + 2:
			exit(1)
		elif choice == len(menu) + 1:
			go_back = True
		else:
			place_order(res_id, choice-1)

def view_restaurants():
	go_back = False
	while not go_back:

		try:
			restaurants, err = hungry_server.get_restaurants()	
			if type(err) == str:
				print(err)
			elif err:
				raise ValueError
		except:
			print("Cannot connect to server currently, please try again later")
			exit(1)

		choice = make_choice("a restaurants menu to view", list(restaurants.values())+["Go Back"])
		if choice == len(restaurants.values()) + 2:
			exit(1)
		elif choice == len(restaurants.values()) + 1:
			go_back = True
		else:
			view_menu(list(restaurants.keys())[choice-1])

def make_choice(choice_type, choices):
	option = False
	print()
	print("Please choose " + choice_type + " by entering its corresponding number:")
	for index, choice in enumerate(choices):
		print("		" + str(index+1) + ")	" + choice)
	print("		"+str(len(choices)+1)+")	Quit")

	while not option:
		try:
			option = int(input(">	"))
			if option not in range(1, len(choices)+2):
				option = False
				print("	Invalid option number entered")
		except:
			print("	Invalid option number entered")

	return option	

def main():
	option = False
	while option != 3:
		option = make_choice("an option", ["View Restaurants", "View Orders"])
		if option == 1:
			view_restaurants()
		elif option == 2:
			view_orders()
		elif option == 3:
			exit(1)

user_id = None
hungry_server = Pyro4.Proxy("PYRONAME:hungry_server.front_end")
main()
