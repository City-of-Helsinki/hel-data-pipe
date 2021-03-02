from rest_framework import pagination


class CursorTimePagination(pagination.CursorPagination):
    ordering = '-time'
    page_size = 1000

class CursorCreatedAtPagination(pagination.CursorPagination):
    ordering = '-created_at'
    page_size = 1000
