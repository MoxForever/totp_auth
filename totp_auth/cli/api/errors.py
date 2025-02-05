class TotpHttpApiException(Exception):
    pass


class InvalidRequestException(TotpHttpApiException):
    pass


class ServerDownException(TotpHttpApiException):
    pass
