import mysql.connector 
import smtplib 
from email.mime.text import MIMEText 
from email.mime.multipart import MIMEMultipart 
from datetime import datetime 

def connect_db(): 
    try: 
        conn = mysql.connector.connect( 
            host="localhost", 
            user="root", 
            password="12345", 
            database="election_db" 
        ) 
        print("Database connection successful") 
        return conn 
    except mysql.connector.Error as err: 
        print(f"Error: {err}") 
        return None 

def fetch_voters(conn): 
    try: 
        cursor = conn.cursor() 
        cursor.execute("SELECT id, name, email, has_voted FROM voters WHERE has_voted = 0") 
        voters = cursor.fetchall() 
        print(f"Fetched {len(voters)} voters") 
        return voters 
    except mysql.connector.Error as err: 
        print(f"Error: {err}") 
        return [] 

def update_vote_count(conn, candidate): 
    try: 
        cursor = conn.cursor() 
        cursor.execute("UPDATE votes SET count = count + 1 WHERE candidate = %s", (candidate,)) 
        conn.commit() 
        print(f"Updated vote count for {candidate}") 
    except mysql.connector.Error as err: 
        print(f"Error: {err}") 

def mark_voter_as_voted(conn, voter_id): 
    try: 
        cursor = conn.cursor() 
        cursor.execute("UPDATE voters SET has_voted = 1 WHERE id = %s", (voter_id,)) 
        conn.commit() 
        print(f"Marked voter {voter_id} as voted") 
    except mysql.connector.Error as err: 
        print(f"Error: {err}") 

def send_email(voter_email, voter_name): 
    sender_email = "your_email@gmail.com" 
    sender_password = "your_password" 

    message = MIMEMultipart("alternative") 
    message["Subject"] = "Vote Confirmation" 
    message["From"] = sender_email 
    message["To"] = voter_email 

    text = f"Hi {voter_name},\n\nThank you for voting.\n\nDate and Time: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}\n\nBest Regards,\nElection Commission" 
    part = MIMEText(text, "plain") 
    message.attach(part) 

    try: 
        with smtplib.SMTP_SSL("smtp.gmail.com", 465) as server: 
            server.login(sender_email, sender_password) 
            server.sendmail(sender_email, voter_email, message.as_string()) 
        print(f"Email sent to {voter_email}") 
    except smtplib.SMTPException as e: 
        print(f"Error sending email to {voter_email}: {e}") 

def generate_report(conn): 
    try: 
        cursor = conn.cursor() 
        cursor.execute("SELECT candidate, count FROM votes") 
        rows = cursor.fetchall() 
        with open("vote_report.txt", "w") as file: 
            for row in rows: 
                file.write(f"Candidate: {row[0]}, Votes: {row[1]}\n") 
                print(f"Candidate: {row[0]}, Votes: {row[1]}") 
        print("Generated vote report successfully") 
    except mysql.connector.Error as err: 
        print(f"Error: {err}") 

def main(): 
    conn = connect_db() 
    if conn is None: 
        print("Failed to connect to the database") 
        return 

    voters = fetch_voters(conn) 

    for voter in voters: 
        voter_id, voter_name, voter_email, has_voted = voter 
        if not has_voted: 
            print(f"Processing vote for {voter_name}") 
            candidate = input(f"Voter {voter_name}, please enter your vote: ") 
            update_vote_count(conn, candidate) 
            mark_voter_as_voted(conn, voter_id) 
            send_email(voter_email, voter_name) 

    generate_report(conn) 
    conn.close() 
    print("Process completed") 

if __name__ == "__main__": 
    main()
