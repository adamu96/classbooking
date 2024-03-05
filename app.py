import os
from flask import Flask, render_template, request, session, url_for, redirect, flash
from google.cloud import bigquery
import better

client = bigquery.Client.from_service_account_json('credentials/key.json')
app = Flask(__name__, )
app.config['SECRET_KEY'] = 'margrets-legs-221122'

# better credentials
auth = 'Bearer v4.local.EKvZbFP4m02EQHaGJzp-J3nzRPCx_rPl_zrBTfbDH-xn5BC1oDZb1yvYup9sJAO94OxRrmYJcSYuP44Qy3aFl3LnVmPCYkiWOvhcvc2sKxtf3L-Jm5qFBlu7rvng6s2JlXB5bwDR1Edni0H92Kq-9eF_qI6MoVC3lW8RbIN1sxuBEwO409_OWylGyf-WW6Clghp-3czmAq7SlZzfUA'
member_id = 2945507


@app.route('/', methods=['GET', 'POST'])
def login():
    user_data = client.query('SELECT * FROM `classbooking-414412.classbooking_data.user`;').to_dataframe()

    if request.method == 'POST':
        if not user_data[user_data['email'] == [request.form['username']]].empty:
            if user_data[user_data['email'] == request.form['username']].password.values[0] == request.form['password']:
                session['user'] = user_data[user_data['email'] == request.form['username']].first_name.values[0]
                return redirect(url_for('home'))
            else:
                flash('Password Incorrect.')
        else:
            flash('Email Address does not exist, please contact admin.')

    return render_template('login.html')

@app.route('/logout')
def logout():
    session.clear
    return redirect(url_for('login'))

@app.route('/home')
def home():
    if not session:
        flash('Please login.')
        return redirect(url_for('login'))
    
    bookings = better.viewBookings(auth)

    availability = better.getAvailableDates(auth)
    days = ['Monday', 'Tuesday', 'Wednesday', 'Thursday', 'Friday', 'Saturday', 'Sunday']
    
    preference_data = client.query('SELECT * FROM `classbooking-414412.classbooking_data.preferences`;').to_dataframe()
    preference_data['weekdayhour'] = preference_data['day'] + preference_data['slot'].astype(str)

    return render_template('home.html', bookings=bookings, availability=availability, days=days, preference_data=preference_data)


if __name__ == "__main__":
    app.run(debug=True,host='0.0.0.0',port=int(os.environ.get('PORT', 8080)))