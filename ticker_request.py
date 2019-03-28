from flask_wtf import Form
from wtforms import TextField, IntegerField, TextAreaField, SubmitField, RadioField, SelectField, BooleanField
from wtforms import validators, ValidationError

class TickerInputs(Form):
   ticker = TextField("Stock Ticker:", [validators.DataRequired(
       "Please enter a valid stock ticker.")], default='GOOG')

   opening = BooleanField('Opening Price')
   closing = BooleanField('Closing Price')
   high = BooleanField('High Price')
   low = BooleanField('Low Price')
   adj_opening = BooleanField('Adjusted Opening Price')
   adj_closing = BooleanField('Adjusted Closing Price')
   adj_high= BooleanField('Adjusted High Price')
   adj_low= BooleanField('Adjusted Low Price')

   submit = SubmitField("Generate Plot(s)")
