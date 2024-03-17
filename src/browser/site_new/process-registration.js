const sqlite3 = req('sqlite3').verbose();
const db = new sqlite3.db('users.db');

const username = req.body.username;
const email = req.body.email;
const password = req.body.password;


db.serialize(() => {
    db.run("INSERT INTO users (user_name, email, password_user) VALUES (?, ?, ?), [username, email, password]", function(err) {
        if (err) {
            console.error(err.message);
            return;
        }
        console.log('New record created successfully');
    });
});

db.close();