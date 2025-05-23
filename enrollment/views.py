from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework import status, generics
from rest_framework.permissions import IsAuthenticated
from django.contrib.auth import get_user_model, authenticate
from django.shortcuts import get_object_or_404

from .models import *
from .serializers import *
User = get_user_model()

# =========================
# USER REGISTRATION & LOGIN
# =========================


class RegisterUser(APIView):
    def post(self, request):
        serializer = UserSerializer(data=request.data)

        role = request.data.get("role")
        if role not in ["student", "teacher"]:
            return Response({"error": "Role must be 'student' or 'teacher'."}, status=status.HTTP_400_BAD_REQUEST)

        if serializer.is_valid():
            user = serializer.save()
            return Response(serializer.data, status=status.HTTP_201_CREATED)

        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)



class LoginUser(APIView):
    def post(self, request):
        try:
            username = request.data.get('username')
            password = request.data.get('password')

            user = authenticate(username=username, password=password)
            if user:
                serializer = UserSerializer(user)
                return Response(serializer.data, status=status.HTTP_200_OK)
            return Response({"message": "Invalid credentials"}, status=status.HTTP_401_UNAUTHORIZED)
        except Exception as e:
            return Response({"error": str(e)}, status=status.HTTP_500_INTERNAL_SERVER_ERROR)



class UserListView(generics.ListAPIView):
    serializer_class = UserListSerializer

    def get_queryset(self):
        queryset = User.objects.all()
        role = self.request.query_params.get('role')
        department = self.request.query_params.get('department')
        username = self.request.query_params.get('username')

        if role:
            queryset = queryset.filter(role=role)
        if department:
            queryset = queryset.filter(department__icontains=department)
        if username:
            queryset = queryset.filter(username__icontains=username)

        return queryset

# =====================
# SUBJECT CRUD OPERATIONS
# =====================

class SubjectListCreateAPIView(APIView):
    permission_classes = [IsAuthenticated]

    def get(self, request):
        subjects = Subject.objects.all()
        serializer = SubjectSerializer(subjects, many=True)
        return Response(serializer.data)

    def post(self, request):
        serializer = SubjectSerializer(data=request.data)
        if serializer.is_valid():
            serializer.save()
            return Response(serializer.data, status=status.HTTP_201_CREATED)
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)

class SubjectDetailAPIView(APIView):
    permission_classes = [IsAuthenticated]
    serializer_class = SubjectSerializer

    def get(self, request, pk):
        subject = get_object_or_404(Subject, pk=pk)
        serializer = self.serializer_class(subject)
        return Response(serializer.data)

    def patch(self, request):
        try:
            subject_id = request.data.get("id")
            if not subject_id:
                return Response({"error": "ID is required for partial update"}, status=status.HTTP_400_BAD_REQUEST)

            subject_obj = Subject.objects.get(id=subject_id)
            serializer = self.serializer_class(subject_obj, data=request.data, partial=True)
            if serializer.is_valid():
                serializer.save()
                return Response({"data": serializer.data}, status=status.HTTP_200_OK)
            return Response({"error": serializer.errors}, status=status.HTTP_400_BAD_REQUEST)
        except Subject.DoesNotExist:
            return Response({"error": "Subject not found"}, status=status.HTTP_404_NOT_FOUND)
        except Exception as e:
            return Response({"error": str(e)}, status=status.HTTP_500_INTERNAL_SERVER_ERROR)

    def delete(self, request, pk):
        subject = get_object_or_404(Subject, pk=pk)
        subject.delete()
        return Response(status=status.HTTP_204_NO_CONTENT)

# =====================
# ENROLLMENT APIs
# =====================

class EnrollmentListCreateAPIView(APIView):
    permission_classes = [IsAuthenticated]

    def get(self, request):
        student_id = request.query_params.get('student_id')
        if not student_id:
            return Response({"error": "student_id query param is required"}, status=status.HTTP_400_BAD_REQUEST)

        enrollments = Enrollment.objects.filter(student_id=student_id)
        serializer = EnrollmentSerializer(enrollments, many=True)
        return Response(serializer.data)

    def post(self, request):
        subject_id = request.data.get('subject_id')
        if not subject_id:
            return Response({"error": "subject_id is required"}, status=status.HTTP_400_BAD_REQUEST)

        user = request.user
        try:
            student = Student.objects.get(user=user)
            subject = Subject.objects.get(id=subject_id)
        except Student.DoesNotExist:
            return Response({"error": "Student not found"}, status=status.HTTP_404_NOT_FOUND)
        except Subject.DoesNotExist:
            return Response({"error": "Subject not found"}, status=status.HTTP_404_NOT_FOUND)

        if Enrollment.objects.filter(student=student, subject=subject).exists():
            return Response({"error": "Already enrolled in this subject"}, status=status.HTTP_400_BAD_REQUEST)

        enrollment = Enrollment.objects.create(student=student, subject=subject)
        serializer = EnrollmentSerializer(enrollment)
        return Response(serializer.data, status=status.HTTP_201_CREATED)
