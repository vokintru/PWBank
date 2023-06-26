from PyEasyQiwi import QiwiConnection


class QiwiPay:
    def __init__(self, api_key):
        self.conn = QiwiConnection(api_key)

    def create_bill(self, value, user_id, comment):
        pay_url, bill_id, response = self.conn.create_bill(value=value,
                                                           delay=30,
                                                           description=f'{user_id}',
                                                           comment=comment,
                                                           )
        return pay_url, bill_id

    def check_bill(self, bill_id):
        status, response = self.conn.check_bill(bill_id)
        if status == 'PAID':
            self.conn.remove_bill(bill_id)
            return 'PAID'
        elif status == 'WAITING':
            return 'WAITING'
        elif status == 'REJECTED':
            self.conn.remove_bill(bill_id)
            return 'REJECTED'
        elif status == 'EXPIRED':
            self.conn.remove_bill(bill_id)
            return 'EXPIRED'

    def close_bill(self, bill_id):
        self.conn.remove_bill(bill_id)
