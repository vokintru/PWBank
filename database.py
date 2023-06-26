import sqlite3


class BotDB:
    def __init__(self, db_file):
        self.conn = sqlite3.connect(db_file)
        self.data = self.conn.cursor()

    def user_exists(self, user_id):
        result = self.data.execute("SELECT `id` FROM `users` WHERE `user_id` = (?)", (user_id,))
        x = bool(len(result.fetchall()))
        if x == 1:
            return False
        else:
            return True

    def user_exists_username(self, user_name):
        result = self.data.execute("SELECT `id` FROM `users` WHERE `user_name` = (?)", (user_name,))
        x = bool(len(result.fetchall()))
        if x == 1:
            return False
        else:
            return True

    def check_ban(self, user_id):
        result = self.data.execute('SELECT `banned` FROM `users` WHERE `user_id` = ?', (user_id,))
        result = result.fetchone()[0]
        if result == 0:
            return True
        else:
            return False

    def get_user_name(self, user_id):
        result = self.data.execute('SELECT `user_name` FROM `users` WHERE `user_id` = ?', (user_id,))
        return result.fetchone()[0]

    def get_user_id(self, user_name):
        result = self.data.execute('SELECT `user_id` FROM `users` WHERE `user_name` = ?', (user_name,))
        return result.fetchone()[0]

    def get_balance(self, user_id):
        result = self.data.execute('SELECT `balance` FROM `users` WHERE `user_id` = ?', (user_id,))
        return result.fetchone()[0]

    def get_card(self, user_id):
        result = self.data.execute('SELECT `card` FROM `users` WHERE `user_id` = ?', (user_id,))
        return result.fetchone()[0]

    def add_user(self, user_id, user_name):
        self.data.execute('INSERT INTO `users` (`user_id`, `user_name`) VALUES (?, ?)',
                          (user_id, user_name))
        self.data.execute('INSERT INTO `promo` (`user_id`, `promos`) VALUES (?, ?)', (user_id, ''))
        self.data.execute('INSERT INTO `settings` (`user_id`) VALUES (?)', (user_id, ))
        return self.conn.commit()

    def add_promo(self, user_id, promo):
        x = self.data.execute('SELECT `promos` FROM `promo` WHERE `user_id` = ?', (user_id,))
        x = str(x.fetchall())[3:-4].split()
        x.append(promo)
        promos = ' '.join(x)
        self.data.execute("UPDATE `promo` SET `promos` = ? WHERE `user_id` = ?", (promos, user_id))
        self.conn.commit()

    def promos(self, user_id):
        x = self.data.execute('SELECT `promos` FROM `promo` WHERE `user_id` = ?', (user_id,))
        x = str(x.fetchall())[3:-4]
        return x

    def get_all_user_id(self):
        x = self.data.execute('SELECT `user_id` FROM `users`').fetchall()
        y = []
        for i in range(len(x)):
            y.append(x[i][0])
        return y

    def add_money(self, user_id, value):
        x = self.data.execute('SELECT `balance` FROM `users` WHERE `user_id` = ?', (user_id,))
        x = str((x.fetchall()))[2:-3]
        if x == 'None':
            self.data.execute("UPDATE `users` SET `balance` = ? WHERE `user_id` = ?", (value, user_id,))

        else:
            x = float(x)
            x += float(value)
            self.data.execute("UPDATE `users` SET `balance` = ? WHERE `user_id` = ?", (x, user_id,))
        self.conn.commit()

    def link(self, user_id, card):
        self.data.execute("UPDATE `users` SET `card` = ? WHERE `user_id` = ?", (card, user_id,))
        self.data.execute("UPDATE `users` SET `status` = ? WHERE `user_id` = ?", (1, user_id,))
        self.conn.commit()

    def status(self, user_id):
        x = self.data.execute('SELECT `status` FROM `users` WHERE `user_id` = ?', (user_id,))
        x = float(str(x.fetchall())[2:-3])
        return x

    def set_status(self, user_id, status):
        self.data.execute('UPDATE `users` SET `status` = ? WHERE `user_id` = ?', (status, user_id))
        self.conn.commit()

    def set_ban_status(self, user_id):
        self.data.execute('UPDATE `users` SET `banned` = ? WHERE `user_id` = ?', (1, user_id))
        self.conn.commit()

    def update_username(self, user_id, user_name):
        self.data.execute('UPDATE `users` SET `user_name` = ? WHERE `user_id` = ?', (user_name, user_id))
        self.conn.commit()

    def get_keyboard(self, user_id):
        x = self.data.execute('SELECT `keyboard_mode` FROM `settings` WHERE `user_id` = ?', (user_id,))
        x = int(x.fetchall()[0][0])
        return x

    def set_keyboard(self, user_id, id):
        self.data.execute('UPDATE `settings` SET `keyboard_mode` = ? WHERE `user_id` = ?', (id, user_id))
        self.conn.commit()

    def get_public_status(self, user_id):
        x = self.data.execute('SELECT `public` FROM `settings` WHERE `user_id` = ?', (user_id,))
        x = float(str(x.fetchall())[2:-3])
        return x

    def set_public_status(self, user_id, id):
        self.data.execute('UPDATE `settings` SET `public` = ? WHERE `user_id` = ?', (id, user_id))
        self.conn.commit()

    def get_all_public_user_id(self):
        x = self.data.execute('SELECT `user_id` FROM `settings` WHERE `public` = ?', (1, )).fetchall()
        y = []
        for i in range(len(x)):
            y.append(x[i][0])
        return y

    def close(self):
        self.conn.close()
