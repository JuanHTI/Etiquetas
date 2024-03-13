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
#import astunparse
#import re
#import pandas 

#from six.moves import cStringIO


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
        conn = http.client.HTTPSConnection('api.pipedream.com')
        conn.request("GET", '/v1/sources/dc_76uX6Kw/event_summaries', '', {
        'Authorization': 'Bearer c801ee561fd1ab11dfb5e9c4a75a61ca',
        })
        
        res = conn.getresponse()
        data = res.read()
        #dado recebe o json completo dos 100 requisição feita ao webhook
        dado = json.loads(data)
        contador = dado['page_info']['total_count']
        
        #if contador == 0:
        #else:
        try:    #    print('Continuar...')
            if contador > 0:
                #No for estou passando por todos os campos do json/dado para pegar cada uma das chamadas
                for i in range(contador):
                    info('-------------LOG-------------')                    
                    #O contador já vem com a formatacao para pegar as requisiçoes 
                    contador -= 1
                    id_1 = dado['data'][contador]
                    
                    #Nessa pegamos o valor da ultima 100 requisicao que fizerao para nosso webhook
                    #E colocamos em uma variavel global (self.id)
                    id = id_1['event']['body']['content']['id']
                    #Aqui pegamos o id do ultimo das 100 eventos feitas e coloca em uma variavel (self.delet)
                    #Para ao final de todos o processo fazer a exclucao 
                    nome = 'token.json'
                    with open(nome, 'r') as arquivo:
                        tokengumga= json.load(arquivo)
                    
                    token = id_1['event']['body']['content']['oi'].replace(".", "")
                    gumgaToken = tokengumga[token] 
                    delet = id_1['id']
                    #info(token, gumgaToken)
                    info(f'{i} - ({delet} id: {id} oi: {token})')
                    #self.Log = f'Acesso realizado com sucesso!! /n {dado.status_code, dado.text}'
                    #Colocamos um time de 3 segundos para continuar 
                    time.sleep(0.5)
                    #Nessa variavel de anbiente, passo para ela o numero da requisição, e passo para ele o id e o horario atual
                    info('Foi concluido com sucesso!')
                    #jo.LOG(log1)
                    jo.NAME(delet, id, i, gumgaToken)
                    #jo.LOG() 
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
                #os.system('cls')
                #sys.stdout.flush()
                
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
                                break
                            elif xref >= 30:
                                page_with_qr = page_num
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
                if response.status_code == 422:
                    jo.DELETE(delet)
                elif response.text == '{"code":"500","message":"Tipo de entrega não permitido pelo Marketplace."}':
                    print("deu certo")
                    jo.DELETE(delet)
                elif response.text == '{"code":"500","message":"Não é possível emitir etiqueta. Detalhes: O pedido não é da modalidade ENVIOS."}':
                    print("deu certo")
                    jo.DELETE(delet)
                #jo.LOG(LogPDF)
                #jo.DELETE(delet)
        except Exception as e:
            #l = r"[Errno 2] No such file or directory: '\\\\172.16.16.8\\Infraestrutura\\Nova pasta\\35240107293118000609550080000307081931355724.pdf'"
            critical(e)
            #error(e)
            ftp.quit()
    #Nessa api vamos chamaar a api para pegarmos o numero do pedido e renomear o PDF, para outros projetos e ser mais facil de acessar
    def NAME(self, delet, id, i, gumgaToken):
        try:
            url = f'http://api.anymarket.com.br/v2/orders/{id}'
            #token = '70900904L259060318E1770839233074C167752723307400O1.I'
            header = {
                'Content-type':'application/json',
                'gumgaToken': f'{gumgaToken}'
            }
            response = requests.get(url, headers=header)
            t = response.json()
            c = 'accessKey'
            jo.buscar_valor(t, c)
            #info('Numero da etiqueta foi encontrado, com sucesso!')
            nome = self.resultado_recursivo
            #self.nome = t['content'][self.con]['invoice']['accessKey']
            
            if nome == None:
                jo.DELETE(delet)
            else:
                time.sleep(0.5)
                info(f'Codigo do pedido foi encontrado: {nome}')
                jo.PDF(nome, id, delet, i, gumgaToken)
            
        except Exception as e:
            #self.LogNome = f'Codigo do pedido foi encontrado {e, nome}'
            #jo.LOG(LogNome)
            warn(f'Erro em buscar o codigo do pedido: {e}')
            #jo.DELETE(delet)

    #Nessa api vamos deletar o evento que já foi usado na nossa webhook         
    def DELETE(self, deleta):
        try:
            
            conn = http.client.HTTPSConnection('api.pipedream.com')
            conn.request("DELETE", f'/v1/sources/dc_76uX6Kw/events?start_id={deleta}&end_id={deleta}', '', {
            'Authorization': 'Bearer c801ee561fd1ab11dfb5e9c4a75a61ca',
            })
            time.sleep(0.5)
            res = conn.getresponse()
            time.sleep(0.5)
            data = res.read()
            time.sleep(0.5)

            info(f'Foi deletado: {deleta}')
        except Exception as e:
            critical(f'Não foi possivel deletar evento:{e}')
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

#API()
while True:
    jo = API()



#while True:
#    te = API()
#    te.PDF()
#    te.NAME()
#    te.DELETE()
#    te.SAVE_PDF()




