# Image Encryption Program using Unimodular Hill Cipher and AES

This Python program provides a secure and efficient method for image encryption by combining the Unimodular Hill Cipher and AES (Advanced Encryption Standard) algorithms. The goal is to enhance security by leveraging the strengths of both symmetric encryption techniques.

## Features

- **Unimodular Hill Cipher**: This algorithm uses a unimodular matrix for the encryption process. A unimodular matrix is a square integer matrix with a determinant of ±1, ensuring that the matrix is invertible modulo a given integer, which is essential for the decryption process. This method allows for complex transformations of the image data, making it difficult to reverse without the correct key.

- **AES Encryption**: AES is a widely used encryption standard that provides a strong layer of security. By combining AES with the Unimodular Hill Cipher, this program ensures that the image data is encrypted using two different methodologies, adding an extra layer of security.

- **Hybrid Encryption Process**: The program first encrypts the image using the Unimodular Hill Cipher, which scrambles the pixel values. The resulting data is then encrypted again using AES, making the image data highly secure.

- **Decryption Support**: The program supports decryption of the encrypted image using the appropriate keys, ensuring that the original image can be recovered without loss of quality.

- **Flexible Image Support**: The program is designed to work with various image formats, making it versatile for different use cases.

## Installation

To install the required dependency, use the following command:

```bash
pip install pycryptodome
```

## Usage

1. **Run the Program**:
    ```bash
    python main.py
    ```

## License

This project is licensed under the MIT License. See the [LICENSE](LICENSE) file for more details.

## Contributing

Contributions are welcome! Please feel free to submit a Pull Request or open an Issue for any bugs or feature requests.
