import streamlit as st
import pymssql
import os
from config import sql_settings
from product_service import (
    ProductRegistrationError,
    ProductValidationError,
    register_product,
)
from storage import (
    delete_product_image,
    download_product_image,
    upload_product_image,
)


# Azure Blob
CONNECTION_STRING = os.getenv("AZURE_STORAGE_CONNECTION_STRING")
CONTAINER_NAME = os.getenv("AZURE_STORAGE_CONTAINER_NAME")
ACCOUNT_NAME = os.getenv("AZURE_STORAGE_ACCOUNT_NAME")


# Azure SQL
try:
    sql_config = sql_settings()
except ValueError as exc:
    st.error(str(exc))
    st.stop()
SQL_SERVER = sql_config["SQL_SERVER"]
SQL_DATABASE = sql_config["SQL_DATABASE"]
SQL_USERNAME = sql_config["SQL_USERNAME"]
SQL_PASSWORD = sql_config["SQL_PASSWORD"]

# Título da aplicação
st.title("Cadastro de Produto - E-Commerce na Cloud")

# Formulário para cadastro do produto
product_name = st.text_input("Nome do Produto", max_chars=100)
description = st.text_area("Descrição do Produto", max_chars=255)
price = st.number_input(
    "Preço do Produto", min_value=0.0, max_value=99999999.99, format="%.2f"
)
uploaded_file = st.file_uploader("Imagem do Produto", type=["png", "jpg", "jpeg"])


def upload_image(file):
    return upload_product_image(
        file, CONNECTION_STRING, ACCOUNT_NAME, CONTAINER_NAME
    )


def delete_image(blob_name):
    delete_product_image(blob_name, CONNECTION_STRING, CONTAINER_NAME)


# Função para inserir os dados do produto no Azure SQL Server usando pymssql
def insert_product_sql(product_data):
    with pymssql.connect(
        server=SQL_SERVER,
        user=SQL_USERNAME,
        password=SQL_PASSWORD,
        database=SQL_DATABASE,
    ) as connection:
        cursor = connection.cursor()
        insert_query = """
        INSERT INTO dbo.Produtos (nome, descricao, preco, imagem_url)
        VALUES (%s, %s, %s, %s)
        """
        cursor.execute(
            insert_query,
            (
                product_data["nome"],
                product_data["descricao"],
                product_data["preco"],
                product_data["imagem_url"],
            ),
        )
        connection.commit()
    return True


# Função para listar os produtos do Azure SQL Server
def list_products_sql():
    try:
        conn = pymssql.connect(server=SQL_SERVER, user=SQL_USERNAME, password=SQL_PASSWORD, database=SQL_DATABASE)
        # Usamos cursor com dict=True para facilitar a conversão para DataFrame
        cursor = conn.cursor(as_dict=True)
        query = "SELECT id, nome, descricao, preco, imagem_url FROM dbo.Produtos"
        cursor.execute(query)
        rows = cursor.fetchall()
        cursor.close()
        conn.close()
        return rows
    except Exception as e:
        st.error(f"Erro ao listar produtos: {e}")
        return []


# Função para exibir a lista de produtos na tela
def list_produtos_screen():
    products = list_products_sql()
    if products:
        # Define o número de cards por linha
        cards_por_linha = 3
        cols = st.columns(cards_por_linha)
        for i, product in enumerate(products):
            col = cols[i % cards_por_linha]
            with col:
                st.markdown(f"### {product['nome']}")
                st.write(f"**Descrição:** {product['descricao']}")
                st.write(f"**Preço:** R$ {product['preco']:.2f}")
                if product["imagem_url"]:
                    try:
                        image = download_product_image(
                            product["imagem_url"],
                            CONNECTION_STRING,
                            ACCOUNT_NAME,
                            CONTAINER_NAME,
                        )
                        st.image(image, width=300)
                    except Exception as exc:
                        st.error(f"Erro ao carregar imagem: {exc}")
                st.markdown("---")
            if (i + 1) % cards_por_linha == 0 and (i + 1) < len(products):
                cols = st.columns(cards_por_linha)
    else:
        st.info("Nenhum produto encontrado.")


# Botão para cadastro do produto
if st.button("Cadastrar Produto"):
    try:
        product_data = register_product(
            product_name,
            description,
            price,
            uploaded_file,
            upload_image,
            insert_product_sql,
            delete_image,
        )
    except ProductValidationError as exc:
        st.warning(str(exc))
    except ProductRegistrationError as exc:
        st.error(str(exc))
    else:
        st.success("Produto cadastrado com sucesso no Azure SQL!")
        list_produtos_screen()
        st.json(product_data)

st.header("Listagem dos Produtos")


# Botão para carregar e exibir a lista de produtos
if st.button("Listar Produtos"):
    list_produtos_screen()
