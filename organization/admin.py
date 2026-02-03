from django.contrib import admin
from .models import MemberProfile,Membership,OrganizationUnit,ProgramStudi,Role,RoleMeta,RolePermission


admin.site.register(MemberProfile)
admin.site.register(Membership)
admin.site.register(OrganizationUnit)
admin.site.register(ProgramStudi)
admin.site.register(Role)
admin.site.register(RoleMeta)
admin.site.register(RolePermission)
# Register your models here.
