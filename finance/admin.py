from django.contrib import admin
from .models import FeePeriod, Payment,FeeType, MemberBill, FinancialTransaction

admin.site.register(FeePeriod)
admin.site.register(Payment)
admin.site.register(FeeType)
admin.site.register(MemberBill)
admin.site.register(FinancialTransaction)

# Register your models here.
