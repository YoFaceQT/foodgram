from rest_framework.pagination import PageNumberPagination


MAX_PAGE_SIZE = 6


class FoodgramPageNumberPagination(PageNumberPagination):
    page_size = MAX_PAGE_SIZE
    page_size_query_param = 'limit'
