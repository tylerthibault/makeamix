import base64

class FileService:
    @staticmethod
    def file_to_base64(file_obj):
        """
        Converts a file-like object to a base64 encoded string.

        :param file_obj: File-like object (e.g., from Flask's request.files) or None
        :return: Base64 encoded string or None if no file provided
        """
        if file_obj is None or file_obj.filename == '':
            return None
            
        file_content = file_obj.read()
        encoded = base64.b64encode(file_content).decode('utf-8')
        return encoded