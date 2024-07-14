from .exception.document_exception import DocumentException
class DocumentHelper():
    def upload(file, name, s3):
        if file is None:
            raise DocumentException("File is required")
        if name is None:
            raise DocumentException("Username is required")
        if s3 is None:
            raise DocumentException("S3 object is required")
        filename = name.username+"_picture.jpg"
        image_data = file
        try:
            object = s3.Object('x23101083-carinsurance', filename)
            val = object.put(ACL='public-read',Body=image_data,Key=filename)
            print('response from document upload: ', val)
            return filename
        except Exception as e:
            raise DocumentException("Error uploading image to s3")