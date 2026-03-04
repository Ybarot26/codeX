from rest_framework import serializers

from employee.models import Employee


class EmployeeRegistrationSerializer(serializers.ModelSerializer):
    class Meta:
        model = Employee
        fields = ["employee_id",
                  "store_id",
                  "employee_name",
                  "employee_email",
                  "employee_password"]


class FetchEmployeeDetailsSerializer(serializers.ModelSerializer):
    class Meta:
        model = Employee
        fields = ["employee_id",
                  "store_id",
                  "employee_name",
                  "employee_email",
                  "employee_password",
                  "employee_address",
                  "employee_contact_number",
                  "employee_langauges",
                  "employee_skills",
                  "employee_charges"]
        read_only_fields = fields


class EmployeeDetailsManagementSerializer(serializers.ModelSerializer):
    class Meta:
        model = Employee
        fields = ["employee_id",
                  "store_id",
                  "employee_name",
                  "employee_email",
                  "employee_password",
                  "employee_address",
                  "employee_contact_number",
                  "employee_langauges",
                  "employee_skills",
                  "employee_charges"]
