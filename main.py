# importing modules
import mysql.connector as m

# The 's' variable will store user details after successful login/sign-in.
# NOTE: The variable 's' is now only managed in the main application logic,
# and is passed as an argument to functions where needed.

def login():
    """Handles user login."""
    print('-------------------------------------------------')
    # NOTE: User ID, user name, and password inputs are kept for program functionality.
    user_id = int(input("Enter your user ID:"))
    user_name = input("Enter user name:")
    password = int(input("Enter your password:"))
    
    # Connect to the database (hardcoded credentials as per the project)
    mydb = m.connect(host="localhost", user="root", password="gouravbhai@12", database="taj_hotel")
    co = mydb.cursor()
    
    # Check credentials
    co.execute("select * from users")
    user_records = co.fetchall()
  
    s_result = [] # Initialize s_result
    
    for record in user_records:
        # Check if Name (record[1]), Password (record[2]), and ID (record[0]) match the input
        if user_name == record[1] and str(password) == str(record[2]) and user_id == record[0]:
            print("login successful.")
            co.execute('select * from users where UserID={} and UserName="{}" and Password={}'.format(user_id, user_name, password))
            s_result = co.fetchall()
            break
            
    if not s_result: # Check if the result list is empty instead of using jl variable
        print("wrong details given")
        
    mydb.commit()
    print('-------------------------------------------------')
    return s_result # Return the user details

def room_booking(user_details):
    """Handles room booking process.
    Takes user_details (s) as argument."""
    print('-------------------------------------------------')
    mydb = m.connect(host="localhost", user="root", password="gouravbhai@12", database="taj_hotel")
    co = mydb.cursor()
    co.execute('select * from roombooking ')
    booking_records = co.fetchall()
    
    room_num_input = int(input("Enter your selected Room Number: "))
    
    # Logic to generate next Booking ID
    booking_id = booking_records[-1][1] + 1 if booking_records else 1001
    print("Your Booking ID is", booking_id)
    
    u_id = user_details[0][0] # user's id
    u_name = user_details[0][1] # user's name
    address = input("Enter Address: ")
    phone_num = int(input("Enter Phone number:"))
    check_in_date = input('Enter check in date (YYYY-MM-DD):')
    check_out_date = input('Enter check out date (YYYY-MM-DD):')
    gender = input('Enter your gender: ')
    
    co.execute('select RoomNum, Status from rooms')
    room_statuses = co.fetchall()
    
    room_found = False # Tracks if room number was found
    
    for room_record in room_statuses:
        room_num_db = room_record[0]
        # .capitalize() ko .upper() se badla gaya hai
        status = room_record[1].strip().upper() 
        
        if room_num_db == room_num_input:
            room_found = True # Room number found in DB
            
            if status == 'VACANT': # Compare to uppercase status
                # Insert into roombooking (Room_Num, Booking_ID, User_ID, User_Name, Address, Phone_Num, CheckIn, Cheak Out, Gender)
                co.execute("insert into roombooking values({},{},{},'{}','{}',{},'{}','{}','{}')".format(room_num_input, booking_id, u_id, u_name, address, phone_num, check_in_date, check_out_date, gender))
                # Update room status to Occupied
                co.execute("update rooms set Status='{}' where RoomNum={}".format('Occupied', room_num_input))
                print('Room booked.')
                break
            elif status == 'OCCUPIED': # Compare to uppercase status
                print('''Room chosen is already booked by someone.
Please choose another room. ''')
                break
    
    if not room_found:
        print('Entered room number does not exist.')
        
    mydb.commit()
    print('-------------------------------------------------')

def room_details():
    """Displays all room details from the 'rooms' table."""
    print('-------------------------------------------------')
    mydb = m.connect(host="localhost", user="root", password="gouravbhai@12", database="taj_hotel")
    co = mydb.cursor()
    co.execute('select * from rooms')
    room_records = co.fetchall()
    for record in room_records:
        print(record)
    mydb.commit()
    print('-------------------------------------------------')

def menu():
    """Displays the restaurant menu."""
    print('-------------------------------------------------')
    mydb = m.connect(host="localhost", user="root", password="gouravbhai@12", database="taj_hotel")
    co = mydb.cursor()
    print("*****MENU*****")
    print('item_number, item_name, price, category, availability')
    co.execute('select * from menu')
    menu_records = co.fetchall()
    for record in menu_records:
        print(record)
    mydb.commit()
    print('-------------------------------------------------')

def order(user_details):
    """Handles the food ordering process.
    Takes user_details (s) as argument."""
    if not user_details:
        print("Please log in or sign up first.")
        return

    print('-------------------------------------------------')
    mydb = m.connect(host="localhost", user="root", password="gouravbhai@12", database="taj_hotel")
    co = mydb.cursor()
    u_id = user_details[0][0] # user id
    
    # Determine the table number (Logic updated to check booking or ask)
    co.execute('select TableNum from table_booking where UserID = {} ORDER BY Date DESC, Time DESC LIMIT 1'.format(u_id))
    table_result = co.fetchone()
    
    if table_result:
        table_num = table_result[0]
        print("Your Table Number is", table_num)
    else:
        table_num = int(input("Enter your Table Number (must be already booked/assigned): "))

    co.execute('select * from order_info')
    order_info_records = co.fetchall()
    
    # Generate next Order Number
    order_num = len(order_info_records) + 1 
    
    co.execute('select * from menu')
    menu_dishes = co.fetchall() # all dishes
    
    distinct_items_count = int(input("Enter no. of distinct items to be ordered: "))
    total_amount = 0 # Total amount
    
    for i in range(distinct_items_count):
        item_num_input = int(input("Enter the item number to be ordered: "))
        quantity = int(input("Enter the quantity of above item to be ordered: "))
        
        item_found = False
        for dish in menu_dishes:
            if item_num_input == dish[0]: # ItemNum matches
                price = dish[2] # price of a dish
                subtotal = price * quantity # subtotal
                
                # Insert into order_details (OrderNum, ItemNum, Quantity, Subtotal)
                co.execute('insert into order_details values({},{},{},{})'.format(order_num, item_num_input, quantity, subtotal))
                total_amount = total_amount + subtotal
                item_found = True
                break
        
        if not item_found:
            print(f"Item number {item_num_input} not found in menu. Skipping.")
            
    # Insert into order_info (OrderNum, User_ID, Table_Num, Total_Amount)
    co.execute('insert into order_info values({},{},{},{})'.format(order_num, u_id, table_num, total_amount))
    
    mydb.commit()
    print('Your order has been placed. Total Amount: {}'.format(total_amount))
    print('-------------------------------------------------')

def table_booking(user_details):
    """Handles restaurant table booking. Takes user_details (s) as argument."""
    if not user_details:
        print("Please log in or sign up first.")
        return

    print('-------------------------------------------------')
    mydb = m.connect(host="localhost", user="root", password="gouravbhai@12", database="taj_hotel")
    co = mydb.cursor()
    
    table_num = int(input('Enter Table number:'))
    u_id = user_details[0][0] # user id
    date_booked = input('Enter date booked (YYYY-MM-DD): ')
    time_booked = input('Enter time booked (HH:MM:SS): ')
    
    # Insert into table_booking (TableNum, User_ID, Date, Time)
    co.execute('insert into table_booking values({},{},"{}","{}")'.format(table_num, u_id, date_booked, time_booked))
    print('Table booked.')
    mydb.commit()
    print('-------------------------------------------------')

def feedback(user_details):
    """Handles the user feedback submission.
    Takes user_details (s) as argument."""
    if not user_details:
        print("Please log in or sign up first.")
        return

    print('-------------------------------------------------')
    mydb = m.connect(host="localhost", user="root", password="gouravbhai@12", database="taj_hotel")
    co = mydb.cursor()
    
    user_id = user_details[0][0] 
    user_name = user_details[0][1]
    
    # Get next Feedback ID
    co.execute('SELECT FeedbackID FROM feedback ORDER BY FeedbackID DESC LIMIT 1')
    last_id = co.fetchone()
    feedback_id = last_id[0] + 1 if last_id else 1 
    
    print("Your Feedback ID is", feedback_id)
    
    comment_text = input("Enter your feedback/comment: ")
    rating_score = int(input("Enter a rating (1-5, 5 being best): "))
    
    if not 1 <= rating_score <= 5:
        print("Rating must be between 1 and 5. Please try again.")
        return

    # Insert into feedback (FeedbackID, UserID, UserName, Comment, Rating)
    # Note: You need a 'feedback' table in your database for this to work.
    co.execute("insert into feedback values({},{},'{}','{}',{})".format(feedback_id, user_id, user_name, comment_text, rating_score))
    
    mydb.commit()
    print('Thank you! Your feedback has been recorded.')
    print('-------------------------------------------------')
    
# --- Room/Booking Functions (roombooking_remove removed) ---
        
def room_booking_details():
    """Shows room booking details for a given UserID."""
    print('-------------------------------------------------')
    mydb = m.connect(host="localhost", user="root", password="gouravbhai@12", database="taj_hotel")
    co = mydb.cursor()
    search_user_id = input("enter userid to view booking details:")
    co.execute("select * from roombooking where UserID={} ".format(search_user_id))
    results = co.fetchall()
    for record in results: print(record)
    print("details shown")
    mydb.commit()
    print('-------------------------------------------------')

# --- Menu Functions ---
def add_dish():
    """Adds a new dish to the menu."""
    print("__________________________________________")
    mydb = m.connect(host="localhost", user="root", password="gouravbhai@12", database="taj_hotel")
    co = mydb.cursor()
    item_num = int(input("enter item number:"))
    item_name = input("enter item Name:")
    price = int(input("enter price:"))
    category = input("enter category:")
    veg_nonveg = input("enter veg or non-veg:")
    co.execute("insert into menu values({},'{}',{},'{}','{}')".format(item_num, item_name, price, category, veg_nonveg))
    print("dish successfully added ")
    mydb.commit()
    print("--------------------------------------------")

def remove_dish():
    """Removes a dish from the menu by Item Number."""
    mydb = m.connect(host="localhost", user="root", password="gouravbhai@12", database="taj_hotel")
    co = mydb.cursor()
    item_num_to_remove = int(input("Enter item number:"))
    co.execute("delete from menu where ItemNum ={}".format(item_num_to_remove))
    print("dish successfully removed")
    mydb.commit()
    print("--------------------------------------------")

def change_price_dish():
    """Updates the price of a dish."""
    print("--------------------------------------------------")
    mydb = m.connect(host="localhost", user="root", password="gouravbhai@12", database="taj_hotel")
    co = mydb.cursor()
    item_num = int(input("Enter item number to be updated:"))
    new_price = int(input("Enter new price of the dish:"))
    co.execute("update menu set Price={} where ItemNum={}".format(new_price, item_num))
    mydb.commit()
    print("--------------------------------------------------")

def change_name_dish():
    """Updates the name of a dish. (Removed as requested previously)"""
    print("Function to change dish name has been removed.")
    pass
    
def order_details():
    """Displays all order information."""
    mydb = m.connect(host="localhost", user="root", password="gouravbhai@12", database="taj_hotel")
    co = mydb.cursor()
    co.execute("select * from order_info ")
    results = co.fetchall()
    for record in results: print(record)
    print("details shown")
    mydb.commit()
    print("--------------------------------------------")

def cancel_booking(user_details):
    """Cancels the current user's table booking."""
    if not user_details: return
    print("--------------------------------------------------")
    mydb = m.connect(host="localhost", user="root", password="gouravbhai@12", database="taj_hotel")
    co = mydb.cursor()
    u_id = user_details[0][0] # user's id
    co.execute("delete from table_booking where UserID ={}".format(u_id))
    print("Booking cancelled.")
    mydb.commit()
    print("--------------------------------------------")

def book_table(user_details):
    """Books a table for the current user."""
    if not user_details: return
    print("--------------------------------------------------")
    mydb = m.connect(host="localhost", user="root", password="gouravbhai@12", database="taj_hotel")
    co = mydb.cursor()
    u_id = user_details[0][0] # user's id
    table_num = int(input("Enter table number to be booked:"))
    date_booked = input("Enter date for which you want to book table (YYYY-MM-DD):")
    time_booked = input("Enter time (HH:MM:SS):")
    co.execute("insert into table_booking values({},{},'{}','{}')".format(table_num, u_id, date_booked, time_booked))
    print("Table booked.")
    mydb.commit()
    print("--------------------------------------------")
    
# --- Guest Management Functions (Only essential CRUD left) ---
def guest_details():
    """Displays all guest details."""
    print('-------------------------------------------------')
    mydb = m.connect(host="localhost", user="root", password="gouravbhai@12", database="taj_hotel")
    co = mydb.cursor()
    co.execute("select * from guests")
    results = co.fetchall()
    for record in results: print(record)
    print("details shown")
    mydb.commit()
    print('-------------------------------------------------')

def insert_gdetails(user_details):
    """Adds a new guest member's details to the 'guests' table.
    Takes user_details (s) as argument."""
    if not user_details: return
    print("--------------------------------------------------")
    mydb = m.connect(host="localhost", user="root", password="gouravbhai@12", database="taj_hotel")
    co = mydb.cursor()
    u_id = user_details[0][0] # user id
    u_name = user_details[0][1] # user name
    phone_num = int(input("Enter phone number:"))
    address = input("Enter address:")
    gender = input("Enter gender:")
    user_type = "GUEST"
    co.execute("insert into guests values({},'{}',{},'{}','{}','{}')".format(u_id, u_name, phone_num, address, gender, user_type))
    print("data successfully added to database")
    mydb.commit()
    print("--------------------------------------------------")
    
def remove_gdetails():
    """Removes a guest member's details by UserID."""
    print("--------------------------------------------")
    mydb = m.connect(host="localhost", user="root", password="gouravbhai@12", database="taj_hotel")
    co = mydb.cursor()
    guest_id_to_remove = int(input("Enter UserID of the guest to remove: "))
    co.execute("delete from guests where UserID ={}".format(guest_id_to_remove))
    print("data successfully deleted")
    mydb.commit()
    print("--------------------------------------------")

def guest_name_change(user_details):
    """Allows guest to change their name. (Removed as requested previously)"""
    print("Function to change guest name has been removed.")
    return user_details

# --- Removed Functions: guest_phoneNum_change, guest_address_change, search_gname, search_guest ---


# --- About Hotel Text ---
xk = ''' Welcome to TAJ HOTEL, where nature meets luxury in perfect harmony.
Nestled in a serene and picturesque location, TAJ HOTEL offers an unforgettable escape surrounded by breathtaking landscapes and tranquil surroundings.
Whether you’re here to unwind, explore, or indulge in world-class amenities, our hotel provides the ideal setting for relaxation and rejuvenation.
Step outside and be embraced by the beauty of nature — lush gardens, panoramic views, and the soothing sounds of nature create a peaceful oasis right at your doorstep.
Our expertly landscaped grounds are perfect for a leisurely stroll, while nearby hiking trails and scenic spots allow you to connect with the great outdoors.
Inside, our modern, yet cozy accommodations provide a warm and inviting atmosphere, designed to complement the natural beauty that surrounds us.
Large windows offer stunning views of the landscape, bringing the outside in and filling every room with light and fresh air.
From sunrise to sunset, TAJ HOTEL offers a serene escape that blends the comfort of luxury with the peace of nature.
Come experience an environment that nurtures your soul and rejuvenates your spirit.
Whether you’re visiting for a weekend get away or a longer stay, we promise that every moment spent here will be a tranquil retreat from the everyday hustle.
'''

# --- Main Application Logic ---

if __name__ == "__main__":
    
    s = [] # User details variable, locally maintained

    # 1. Login/Sign-in Loop
    while True:
        print('-------------------------------------------------')
        print('Press 1- Login')
        print('Press 2- Sign in')
        print('Press 3- About hotel')
        print('-------------------------------------------------')
        
        
        try:
            choose = int(input("Enter your choice: "))
        except ValueError:
            print('Invalid input. Please enter a number.')
            continue
            
        if choose == 1:
            s_result = login()
            if s_result:
                s = s_result
                # Ensure user is only logged in if they are a GUEST 
                if 'GUEST' in s[0][3].upper().strip():
                    print('Login successful.')
                    break
                else:
                    print('Login successful, but only Guests are supported in this version.')
                    s = [] # clear session for non-guest user
                    print('Please log in with a Guest account.')

            else:
                print('Login failed. Please try again.')
                
        elif choose == 3:
            print(xk)
            
        elif choose == 2: # sign in
            print("--------------------------------------------------")
            mydb = m.connect(host="localhost", user="root", password="gouravbhai@12", database="taj_hotel")
            co = mydb.cursor()

            print('''Don't have any account.
Please create an account.''')
            co.execute('select * from users')
            user_records = co.fetchall()
            # Determine next User ID (assuming sequential)
            new_user_id = user_records[-1][0] + 1 if user_records else 1 
            print('Your user id is', new_user_id)
            
 
            new_user_name = input("Enter user name:")
            new_password = int(input("New password:"))
            confirm_password = int(input("Confirm password:"))
            
            if new_password != confirm_password:
                print('wrong password has been given for confirmation')
                print("Enter correct password")
                confirm_password = int(input("Confirm password:"))
                
            user_identity = 'Guest' # Hardcoded to 'Guest' as Staff is removed
            
            # Insert into users (UserID, UserName, Password, UserType)
            co.execute("insert into users values({},'{}',{},'{}')".format(new_user_id, new_user_name, confirm_password, user_identity.lower()))
            
            address = input("Enter address:")
            phone_num = int(input("Enter Phone number:"))
            gender = input("Enter your gender:")
            user_type_upper = user_identity.strip().upper()
            
            # Only allow Guest sign-up
            if user_type_upper == 'GUEST':
                # Insert into guests (User_ID, User_name, phone_number, address, Gender, User_Type)
                co.execute("insert into guests values({},'{}',{},'{}','{}','{}')".format(new_user_id, new_user_name, phone_num, address, gender, 'Guest'))
            # Removed STAFF sign-up logic
                
            mydb.commit()
            
            print('Your account was created')
            s = [(new_user_id, new_user_name, confirm_password, user_type_upper)]
            print("login successful.")
            print('You have logged in through the account created now')
            print("--------------------------------------------------")
            break

        else:
            print('Invalid choice.
Please enter 1, 2, or 3.')
                

    # 2. Main Menu Loop (Guest Only)
    if s and len(s) > 0:
        hy = s[0][3].upper().strip() # User_Type from 's' variable
        
        # Only GUEST section remains
        if 'GUEST' in hy:
            while True:
            
                print('-------------------------------------------------')
                print('Press 1- Lodging Room')
                print('Press 2- Restaurant')
                print('Press 3- Exit')
                print('-------------------------------------------------')
                
                try:
                    c = int(input("Enter your choice: "))
                except ValueError:
                    print('Invalid input. Please enter a number.')
                    continue
                    
                if c == 1: # Lodging Room
                    # Lodging Room submenu
                    while True:
  
                        print('-------------------------------------------------')
                        print('Lodging room')
                        print("Press 1- Room details")
                        print('Press 2- Room booking')
                        print('Press 3- Exit')
                        print('-------------------------------------------------')
                        
                        try:
                            ch = int(input("Enter your choice: "))
                        except ValueError:
                            print('Invalid input. Please enter a number.')
                            continue
                        
                        if ch == 1:
                            room_details()
                            print("Press 1- Room booking")
                            print('Press 2- Skip')
                            try:
                                cfr = int(input("Enter your choice: "))
                            except ValueError:
                                print('Invalid input. Skipping.')
                                cfr = 2
                       
                            if cfr == 1:
                                room_booking(s)
                            elif cfr == 2:
                                pass
                            
                        elif ch == 2:
                            room_booking(s)
              
                        elif ch == 3:
                            break
                        else:
                            print('Give required input')
                            
                        print('-------------------------------------------------')
                        print("Press 1- Feedback")
                        print('Press 2- Skip')
                        try:
                            kk = int(input("Enter your choice: "))
                        except ValueError:
                            print('Invalid input. Skipping.')
                            kk = 2
                            
                        if kk == 1:
                            feedback(s)
                        elif kk == 2:
                            pass
                        print('-------------------------------------------------')
                        break # Exit the inner Lodging menu loop

                elif c == 2: # Restaurant
                    # Restaurant submenu
                    while True:
               
                        print('Welcome to our restaurant')
                        print('Press 1- Menu')
                        print('Press 2- Order')
                        print('Press 3- Table booking')
                        print('Press 4- Exit')
                        
                        try:
                            ci = int(input('Enter your choice:'))
                        except ValueError:
                            print('Invalid input. Please enter a number.')
                            continue
                        
       
                        if ci == 1:
                            menu()
                        elif ci == 2:
                            order(s)
                        elif ci == 3:
                            table_booking(s)
                        elif ci == 4:
               
                            break
                        else:
                            print('Give required input')
                            
     
                        print('-------------------------------------------------')
                        print("Press 1- Feedback")
                        print('Press 2- Skip')
                        try:
                            kk = int(input("Enter your choice: "))
                        except ValueError:
                            print('Invalid input. Skipping.')
                            kk = 2
                            
                        if kk == 1:
                            feedback(s)
                            break
                        elif kk == 2:
                            pass
                        print('-------------------------------------------------')
                        break # Exit the inner Restaurant menu loop
       
                  
                elif c == 3:
                    break
                else:
                    print('Give required input')
      
        # Removed STAFF main menu section completely
        
    # Final closing message
    print('successfully visited')
    print('''
+++++++++++++++++++++++++++++++++++++++++++
  
*****************THANKS FOR VISITING********************
  
+++++++++++++++++++++++++++++++++++++++++++
 
''')
