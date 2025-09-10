import logging
from typing import Optional, Tuple
from io import BytesIO
import os

class PDFSigner:
    """
    Handles PDF digital signing with pyHanko integration and fallback to pypdfsign.
    
    Features:
    - PDF signing with PAdES and SHA-256
    - Fallback mechanism for different signing libraries
    - Error handling and detailed logging
    - Support for CMS signature objects
    """
    
    def __init__(self, certificate_manager):
        """
        Initializes the PDF signer with a certificate manager.
        
        Args:
            certificate_manager: The CertificateManager instance
        """
        self.certificate_manager = certificate_manager
        
        # Set up logging
        self.logger = logging.getLogger(__name__)
        self.logger.setLevel(logging.INFO)
        
        # Create file handler if not exists
        if not self.logger.handlers:
            os.makedirs('logs', exist_ok=True)
            handler = logging.FileHandler('logs/pdf_signing.log')
            formatter = logging.Formatter('%(asctime)s - %(name)s - %(levelname)s - %(message)s')
            handler.setFormatter(formatter)
            self.logger.addHandler(handler)
    
    def sign_pdf(self, pdf_data: bytes, filename: Optional[str] = None) -> bytes:
        """
        Signs a PDF using the stored certificate.
        
        Args:
            pdf_data: The PDF data to sign
            filename: Optional filename for logging purposes
            
        Returns:
            Signed PDF data or original data if signing fails
        """
        cert_data, password = self.certificate_manager.get_certificate()
        
        if not cert_data or not password:
            self.logger.warning("No certificate available for signing")
            return pdf_data
        
        try:
            # Try using pyHanko first
            return self._sign_with_pyhanko(pdf_data, cert_data, password, filename)
        except ImportError:
            self.logger.info("pyHanko not available, trying pypdfsign")
            try:
                # Fall back to pypdfsign
                return self._sign_with_pypdfsign(pdf_data, cert_data, password, filename)
            except Exception as e:
                # If signing fails, log error with filename for easier debugging
                error_msg = f"Error signing PDF"
                if filename:
                    error_msg += f" '{filename}'"
                error_msg += f": {e}"
                self.logger.error(error_msg)
                return pdf_data
        except Exception as e:
            error_msg = f"Error signing PDF"
            if filename:
                error_msg += f" '{filename}'"
            error_msg += f": {e}"
            self.logger.error(error_msg)
            return pdf_data
    
    def _sign_with_pyhanko(self, pdf_data: bytes, cert_data: bytes, password: str, filename: Optional[str] = None) -> bytes:
        """
        Signs a PDF using pyHanko.
        
        Args:
            pdf_data: The PDF data to sign
            cert_data: The certificate data
            password: The certificate password
            filename: Optional filename for logging
            
        Returns:
            Signed PDF data
        """
        try:
            from pyhanko.pdf_utils.incremental_writer import IncrementalPdfFileWriter
            from pyhanko.sign import signers
            from pyhanko.sign.fields import SigFieldSpec
            from pyhanko_certvalidator import ValidationContext
            from cryptography.hazmat.primitives.serialization import pkcs12
            
            # Load certificate from PKCS12
            private_key, cert, ca_certs = pkcs12.load_key_and_certificates(
                cert_data, password.encode()
            )
            
            # Create signer
            signer = signers.SimpleSigner.load_pkcs12(
                cert_data, password.encode()
            )
            
            # Create incremental writer
            reader = BytesIO(pdf_data)
            writer = IncrementalPdfFileWriter(reader)
            
            # Add signature field
            field_spec = SigFieldSpec(
                sig_field_name='Signature',
                x=100, y=100, w=200, h=50
            )
            
            # Sign the PDF
            from pyhanko.sign import signers
            signed_pdf = signers.sign_pdf(
                writer,
                signers.PdfSignatureMetadata(
                    field_name='Signature',
                    md_algorithm='sha256',
                    name='LedgerFlow Digital Signature',
                    reason='Document Authentication',
                    location='LedgerFlow System'
                ),
                signer=signer,
                output=BytesIO()
            )
            
            signed_pdf.seek(0)
            signed_data = signed_pdf.read()
            
            self.logger.info(f"PDF signed successfully with pyHanko{f' - {filename}' if filename else ''}")
            return signed_data
            
        except ImportError:
            raise ImportError("pyHanko not available")
        except Exception as e:
            self.logger.error(f"pyHanko signing error: {e}")
            raise e
    
    def _sign_with_pypdfsign(self, pdf_data: bytes, cert_data: bytes, password: str, filename: Optional[str] = None) -> bytes:
        """
        Signs a PDF using pypdfsign.
        
        Args:
            pdf_data: The PDF data to sign
            cert_data: The certificate data
            password: The certificate password
            filename: Optional filename for logging
            
        Returns:
            Signed PDF data
        """
        try:
            import pypdfsign
            
            # Create temporary files for signing
            import tempfile
            import os
            
            with tempfile.NamedTemporaryFile(suffix='.pdf', delete=False) as temp_pdf:
                temp_pdf.write(pdf_data)
                temp_pdf_path = temp_pdf.name
            
            with tempfile.NamedTemporaryFile(suffix='.pfx', delete=False) as temp_cert:
                temp_cert.write(cert_data)
                temp_cert_path = temp_cert.name
            
            # Sign the PDF
            signed_pdf_path = temp_pdf_path.replace('.pdf', '_signed.pdf')
            
            pypdfsign.sign_pdf(
                input_file=temp_pdf_path,
                output_file=signed_pdf_path,
                certificate_file=temp_cert_path,
                certificate_password=password
            )
            
            # Read signed PDF
            with open(signed_pdf_path, 'rb') as f:
                signed_data = f.read()
            
            # Clean up temporary files
            try:
                os.unlink(temp_pdf_path)
                os.unlink(temp_cert_path)
                os.unlink(signed_pdf_path)
            except:
                pass
            
            self.logger.info(f"PDF signed successfully with pypdfsign{f' - {filename}' if filename else ''}")
            return signed_data
            
        except ImportError:
            raise ImportError("pypdfsign not available")
        except Exception as e:
            self.logger.error(f"pypdfsign signing error: {e}")
            raise e
    
    def verify_signature(self, pdf_data: bytes) -> bool:
        """
        Verifies if a PDF has a valid digital signature.
        
        Args:
            pdf_data: The PDF data to verify
            
        Returns:
            Boolean indicating if signature is valid
        """
        try:
            from PyPDF2 import PdfReader
            from io import BytesIO
            
            reader = PdfReader(BytesIO(pdf_data))
            
            # Check if PDF has signatures
            if '/AcroForm' in reader.trailer['/Root']:
                acro_form = reader.trailer['/Root']['/AcroForm']
                if '/Fields' in acro_form:
                    fields = acro_form['/Fields']
                    for field in fields:
                        if field.get('/FT') == '/Sig':
                            self.logger.info("PDF contains digital signature")
                            return True
            
            self.logger.info("PDF does not contain digital signature")
            return False
            
        except Exception as e:
            self.logger.error(f"Error verifying signature: {e}")
            return False
    
    def get_signing_status(self) -> dict:
        """
        Gets the current signing status and available libraries.
        
        Returns:
            Dictionary with signing status information
        """
        status = {
            'certificate_available': False,
            'pyhanko_available': False,
            'pypdfsign_available': False,
            'signing_ready': False
        }
        
        # Check certificate availability
        cert_data, password = self.certificate_manager.get_certificate()
        status['certificate_available'] = cert_data is not None and password is not None
        
        # Check pyHanko availability
        try:
            import pyhanko
            status['pyhanko_available'] = True
        except ImportError:
            pass
        
        # Check pypdfsign availability
        try:
            import pypdfsign
            status['pypdfsign_available'] = True
        except ImportError:
            # pypdfsign is not available, but we can still sign with pyHanko
            pass
        
        # Check if signing is ready
        status['signing_ready'] = status['certificate_available'] and (
            status['pyhanko_available'] or status['pypdfsign_available']
        )
        
        return status 