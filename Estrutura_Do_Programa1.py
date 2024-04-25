import http.client

import requests

import json

import time 

import os

import fitz

import logging

from logging import basicConfig, DEBUG, debug, info, error, warn, critical, FileHandler, StreamHandler

from PIL import Image

from pyzbar.pyzbar import decode

from ftplib import FTP

from io import BytesIO



basicConfig(
    level=logging.INFO,
    format='[%(asctime)s]:[%(levelname)s]:%(message)s',
    handlers=[FileHandler("LOGs.txt", "a"), 
              StreamHandler()]
)
class API:
    #Criando o primeiro def que é full, todas as chamadas a API() passa por ele primeiro
    #Nesse def chamaos a api para pegarmos o ID e destribuir para as outras chamadas a api
    def __init__(self):
        #Aqui comecamos a fazer a chamada a api do nosso webhook  
        try:    
            conn = http.client.HTTPSConnection('api.pipedream.com')
            conn.request("GET", '/v1/sources/dc_76uX6Kw/event_summaries', '', {
            'Authorization': 'Bearer 6e60b76741f8563fbae10c97c33b4a84',
            })
            res = conn.getresponse()
            data = res.read()
            #dado recebe o json completo dos 100 requisição feita ao webhook
            dado = json.loads(data)
            contador = dado['page_info']['total_count']
        #Tratamento de erro
        except Exception as e:
            warn('Erro', e)    
            
        try:
            #pegando json e criando variaveis, que serao mudados os valores a cada chamada
            if contador > 0:
                #No for estou passando por todos os campos do json/dado para pegar cada uma das chamadas
                for i in range(contador):
                    info('-------------LOG-------------')                    
                    #O contador ja vem com a formatacao para pegar as requisicoes 
                    contador -= 1
                    id_1 = dado['data'][contador]
                    
                    #Nessa variavel pegamos o valor da ultimas 100 requisicao que fizerao para nosso webhook
                    #E colocamos em uma variavel global id
                    id = id_1['event']['body']['content']['id']
                    #Aqui pegamos o id dos 100 eventos, e incrementando em uma variavel delet
                    #Para ao final de todos o processo fazer a exclucao 

                    #nome = 'Token.json'
                    #with open(nome, 'r') as arquivo:
                    #    tokengumga= json.load(arquivo)
                    
                    token = id_1['event']['body']['content']['oi'].replace(".", "")
                    gumgaToken = id_1['event']['query']['gumgaToken'] 
                    delet = id_1['id']
                    #info(token, gumgaToken)
                    info(f'{i} - ({delet} id: {id} oi: {token})')
                    #self.Log = f'Acesso realizado com sucesso!! /n {dado.status_code, dado.text}'
                    #Colocamos um time de 3 segundos para continuar 
                    time.sleep(0.5)
                    #Nessa variavel de anbiente, passo para ela o numero da requisição, e passo para ele o id e o horario atual
                    info('Foi concluido com sucesso!')
                    jo.NAME(delet, id, i, gumgaToken)
                    
            if contador == 0:
                cont = 10
                ler ='Aguardando ['
                for e in ler:
                    time.sleep(0.5)
                    print(e, end='', flush=True)
                for i in range(cont):
                    print('\033[92m','=>', end='', flush=True,)
                    print('\b'*1, end='', flush=True)
                    time.sleep(0.5)
                    cont += 1
                print('\033[0m',']','\b' * 60, end='  ', flush=True)
                time.sleep(0.5)
                
        #Essa e o final do tratamento de erro
        except Exception as e:
            #Criando essa variavel de anbiente para se der erro incrementar no meu arquivo de LOGs
            error(f'Erro: {e}')
            
            
    #Nessa api vamos chamar a api com o ID do pedido para pegarmos a etiqueta e colocar na nossa pasta de rede intranet    
    def PDF(self, nome, id, delet, i, gumgaToken):
        #info(nome)
        ftp = FTP('108.179.192.233')
        ftp.login(user='etiquetas.anymarket@socialsa.global', passwd='h8uPjAr7x?I_')
        try:
            url = 'https://api.anymarket.com.br/v2/printtag/PDF'
            header = {
                'Content-type':'application/json',
                'gumgaToken': f'{gumgaToken}',
            }
            data = {
                'orders':[f'{id}']
            }
            response = requests.post(url, headers=header, json=data)
            if nome == None:
                ftp.storbinary(f'STOR /ETIQUETAS/PROCESSAR/{id}.pdf', BytesIO(response.content))

                
                #rf'\\172.16.16.8\Infraestrutura\Nova pasta\{id}.pdf'#f'C:\\Users\\j.herculano\\Music\\Nova pasta\\{self.nome}.pdf'#
                #with open(local, 'wb') as f:
                #    f.write(response.content)
                #print(response, response.text)
                info(f'PDF foi salvo com sucesso: {response.text}')
                ftp.quit()
                #jo.LOG(LogPDF)
                time.sleep(0.5)
                jo.DELETE(delet)
            elif response.status_code == 200:
                # 1. Abrir o PDF recebido via API
                po = BytesIO(response.content)
                output_pdf = BytesIO()
                # 2. Identificar se uma página contém um QR code e obter o número da página
                pdf_document = fitz.open(stream=po)
                num_pages = pdf_document.page_count
                page_with_qr = None
                if num_pages == 2:
                    qr_code_found = False
                    for page_num in range(len(pdf_document)):
                        print(page_num)
                        page = pdf_document.load_page(page_num)
                        image_list = page.get_images(full=True)

                        for img_info in image_list:
                            xref = img_info[0]
                            base_image = pdf_document.extract_image(xref)
                            image_bytes = base_image["image"]
                            image = Image.open(BytesIO(image_bytes))

                            decoded_objects = decode(image)
                            if decoded_objects:
                                # Se houver um QR code nesta página, registre o número da página e saia do loop
                                print(page_num)
                                page_with_qr = page_num
                                qr_code_found = True
                                break
                            elif xref >= 30:
                                page_with_qr = page_num
                                qr_code_found = True
                                break
                        if qr_code_found:
                            break
                    if page_with_qr is not None:
                        # Adicionar a página com QR code ao PDF modificado
                        pdf_document.select([page_with_qr])
                        pdf_document.save(output_pdf)

                        # Enviar o PDF resultante com uma página para o servidor FTP
                        output_pdf.seek(0)
                        ftp.storbinary(f'STOR /ETIQUETAS/PROCESSAR/{nome}.pdf', output_pdf)
                        info('Pdf salvo com sucesso!')
                        ftp.quit()
                        jo.DELETE(delet)
                    else:
                        
                        ftp.storbinary(f'STOR /ETIQUETAS/PROCESSAR/{nome}.pdf', BytesIO(response.content))

                        info("Foi baixado o PDF da Shein")
                        ftp.quit()
                        jo.DELETE(delet)
                else:
                    ftp.storbinary(f'STOR /ETIQUETAS/PROCESSAR/{nome}.pdf', po)
                    info('Pdf salvo com sucesso!')
                    ftp.quit()
                        
                    jo.DELETE(delet)
            else:
                error(f'Erro: {response.status_code, response.text}')
                ftp.quit()
            
                mensagem = ['{"code":"500","message":"Erro ao gerar as etiquetas. Detalhes: Para gerar etiquetas todos os pedidos devem estar no status Faturado, os seguintes pedidos',
                '{"code":"500","message":"Erro ao realizar a operação. Entrega ', '{"code":"500","message":"Tipo de entrega não permitido pelo Marketplace."}', 
                '{"code":"500","message":"Não é possível emitir etiqueta. Detalhes: O pedido não é da modalidade ENVIOS."}', '{"code":"500","message":"Status n_o permitido pelo Marketplace."}', 
                '{"code":"500","message":"Status não permitido pelo Marketplace."}', '{"code":"500","message":"Erro ao gerar as etiquetas. Detalhes: Erro 400 Bad Request. Detalhe: \\"Etiqueta do pedido já foi postada.'
                ]

                if response.status_code == 422:
                    jo.DELETE(delet)
                else:
                    for msg in mensagem:
                        if response.text.startswith(msg):
                            print("deu certo")
                            jo.DELETE(delet)
        except Exception as e:
            critical(e)
            ftp.quit()
    #Nessa api vamos chamaar a api para pegarmos o numero do pedido e renomear o PDF, para outros projetos e ser mais facil de acessar
    def NAME(self, delet, id, i, gumgaToken):
        try:
            #URL para fazer a chamada para anymarket mandando o ID da etiqueta
            url = f'http://api.anymarket.com.br/v2/orders/{id}'

            header = {
                'Content-type':'application/json',
                'gumgaToken': f'{gumgaToken}'
            }
            response = requests.get(url, headers=header)
            t = response.json()
            c = 'accessKey'
            #Aqui mandamos nosso json na variavel t e nossa condicao a ser encontrada na variavel c
            #Para um def fazer um loop no json para encontrar a variavel c
            jo.buscar_valor(t, c)
            nome = self.resultado_recursivo

            #Nessa condicao vamos comparar se o nome não tiver nada no caso como (None)
            #Realizaremos direto o Delete desta etiqueta            
            if nome == None:
                time.sleep(0.5)
                info(f'Codigo do pedido foi encontrado: {nome}')
                jo.PDF(nome, id, delet, i, gumgaToken)
                  #jo.DELETE(delet)
            #Se caso o nome tiver algo ele segue com a pesquisa do PDF no def
            else:
                time.sleep(0.5)
                info(f'Codigo do pedido foi encontrado: {nome}')
                jo.PDF(nome, id, delet, i, gumgaToken)
        #Tratamento de erro
        except Exception as e:
            critical(f'Erro em buscar o codigo do pedido: {e}')

    #Nessa def vamos deletar o evento que já foi usado na nossa webhook
    #Se caso der erro e exito ele vai  deletar, para limpar a fila do webhook       
    def DELETE(self, deleta):
        #Comecando o tratamento de erro
        try:
            #Chamada ao pipedream, pasando os paramentros com as variaveis deleta
            #Para fazermos a exclução do evento
            conn = http.client.HTTPSConnection('api.pipedream.com')
            conn.request("DELETE", f'/v1/sources/dc_76uX6Kw/events?start_id={deleta}&end_id={deleta}', '', {
            'Authorization': 'Bearer 6e60b76741f8563fbae10c97c33b4a84',
            })
            time.sleep(0.5)
            res = conn.getresponse()
            time.sleep(0.5)
            data = res.read()
            time.sleep(0.5)

            info(f'Foi deletado: {deleta} - {res.status}')
        #final tratamento de erro
        except Exception as e:
            critical(f'Não foi possivel deletar evento:{e}')
    #Nesse def é o que faz a busca dentro do json 
    def buscar_valor(self, json_data, chave_desejada):
        if isinstance(json_data, dict):
            for chave, valor in json_data.items():
                if chave == chave_desejada:
                    return valor
                self.resultado_recursivo = jo.buscar_valor(valor, chave_desejada)
                if self.resultado_recursivo is not None:
                    return self.resultado_recursivo
        elif isinstance(json_data, list):
            for item in json_data:
                self.resultado_recursivo = jo.buscar_valor(item, chave_desejada)
                if self.resultado_recursivo is not None:
                    return self.resultado_recursivo
        return None

while True:
    jo = API()