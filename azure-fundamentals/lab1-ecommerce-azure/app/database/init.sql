CREATE TABLE dbo.Produtos (
    id INT IDENTITY(1,1) PRIMARY KEY,
    nome NVARCHAR(100) NOT NULL,
    descricao NVARCHAR(255),
    preco DECIMAL(10,2) NOT NULL,
    imagem_url NVARCHAR(255)
);
