# importing os module
from ast import NotIn
from audioop import findfactor
from ipaddress import ip_address
import os
import pathlib
import argparse
import paramiko
import jq
from typing import Counter
from progress.bar import Bar, ChargingBar
import os, time, random
import re
from os import remove


def findString(filePath, host, tipoDir):
    file = open(filePath, 'r')
    matchHost = []

    for line in file:
        host_array = line.split(';')

        if len(host_array) == 6:
            lhost_ip = host_array [0]
            lhost_name = host_array [1]

            if tipoDir == 'ip':
                if lhost_ip == str(host):
                    print('La IP ' + lhost_ip + ' (' +  lhost_name  + ') fue encontrada en el archivo de host ' + str(filePath) )
                    matchHost.append(lhost_ip)      
            if tipoDir == 'name':
                if lhost_name == str(host):
                    print('El HostName ' + lhost_name + ' (' +  lhost_ip  + ') fue encontrada en el archivo de host ' + str(filePath) )
                    matchHost.append(lhost_ip)
            

    
     
    return matchHost


def cargarArchivosHost():


    rootPath = '.'
    directorio = pathlib.Path(rootPath).glob('**/*.lhl')
    
    return directorio
    


def eliminarArchivosHost():
    rootPath = '.'
    directorio = pathlib.Path(rootPath).glob('**/*.lhl')
    for fichero in directorio:
        remove(fichero)

    return directorio

def is_valid_IP(str):
    return bool(re.match(r'^((0|[1-9][0-9]?|1[0-9][0-9]|2[0-4][0-9]|25[0-5])(\.|$)){4}$', str))


def find_host(filePath, host_ip, tipoDir):

    
    if tipoDir == 'all':
        matchHost = findString(filePath, host_ip,'ip')
        if len(matchHost) == 0:
            matchHost = findString(filePath, host_ip,'name')
    else:    
        matchHost = findString(filePath, host_ip,tipoDir)


    if len(matchHost) > 0:
        return matchHost
    else:
        if tipoDir == 'ip':
            print('Ip no encontrada en los archivos de host') 
        if tipoDir == 'name':
            print('Hostname no encontrada en los archivos de host')
        if tipoDir == 'all':
            print('No existe la Ip o el Hostname que concuerde exactamente con algun registro en los archivos de host')
        return matchHost   


def del_host(host_ip, host_name, host_folder):
    state = 'ok'
    return state


def validarVariableEntorno(variableEntorno):
    try:
        varEnviroment = os.environ.get(variableEntorno,'')
    except Exception as e:
        varEnviroment  = ''

    return varEnviroment


def conectar(host_ip):

    commandShell = ''
    
    linky_user = validarVariableEntorno('linky_user')
    linky_password = validarVariableEntorno('linky_password')
    linky_pivot = validarVariableEntorno('linky_pivot')
    
    
    if linky_user == '':
        print ('Falta setear la variable de ambiente linky_user (export linky_user=xxxxx)')
        return False

    if linky_password == '':
        print ('Falta setear la variable de ambiente linky_password (export linky_password=xxxxx)')
        return False


    if linky_user != '' and linky_pivot != '':
        commandShell = 'sshpass -p ' + linky_password + ' ssh -o StrictHostKeyChecking=no -J ' + linky_user + '@' + linky_pivot + ' ' + linky_user  + '@' + str(host_ip)
    else:
        if linky_user != '':
            commandShell = 'sshpass -p ' + linky_password + ' ssh -o StrictHostKeyChecking=no  ' + linky_user + '@' + str(host_ip)
    

    os.system(commandShell)
    os.system('exit')




def tipoJerarquia(nameHost):
    jerarquia = ''
    strHost = ''
    lHost = []
    strRoot = ''
    strGroup = ''
    strSubGroup = ''

    lHost =  nameHost.split('.')
    if len(lHost) > 0:
        strHost = lHost[0]
    else:
        strHost = nameHost

    
    lnameHost = strHost.split('-')
    if len(lnameHost) == 5:
        strRoot = lnameHost[0]  + '-' + lnameHost[1]
        strGroup = lnameHost[2]
        strSubGroup = lnameHost[3] + '-' + lnameHost[4]

    if len(lnameHost) == 4:
        strRoot = lnameHost[0]  + '-' +lnameHost[1]
        strGroup = lnameHost[2]
        strSubGroup = lnameHost[3]

    if len(lnameHost) == 3:
        
        strRoot = lnameHost[0]
        strGroup = lnameHost[1]
        strSubGroup = lnameHost[2]
        if strRoot.upper == 'D':
            strRoot = 'd'

        if strRoot.upper == 'Q':
            strRoot = 'q'

        if strRoot.upper == 'P':
            strRoot = 'p'


    if len(lnameHost) == 2 or len(lnameHost) == 1:
        strShortName = lnameHost[0]
        lShortName = strShortName.split('prod')
        strRoot = 'prod'
        if len(lShortName) == 1:
            lShortName = strShortName.split('qa')
            strRoot = 'qa'
            if len(lShortName) == 1:
                lShortName = strShortName.split('desa')
                strRoot = 'desa'
                if len(lShortName) == 1:
                    lShortName = strShortName.split('adm')
                    strRoot = 'adm'
        if len(lShortName)== 2:
            strGroup = lShortName[0]
            strSubGroup = lShortName[1]
            
    
    if strRoot == '' or strGroup == '' or strSubGroup == '':
        strRoot = 'other'
        strGroup = 'agrupacion'
        strSubGroup = 'subagrupacion'
        
        



    jerarquia = strRoot + ';' + strGroup + ';' + strSubGroup + ';ok'

    return jerarquia



def generarJerarquia(nameHost):

    jerarquia = tipoJerarquia(nameHost)
    
    return jerarquia




def armarComando(busquedaInfoBlox):
    comandoJq = " | jq -r '.[]|.name,.ipv4addrs[].ipv4addr'"
    
    userInfoBlox = 'tsotfprod'
    passwordInfoBlox = 'Tf-123..'
    
    tipoBusqueda=''


    if is_valid_IP(busquedaInfoBlox):
        tipoBusqueda = 'ipv4addr'
    else:
        tipoBusqueda = 'name'

    
    paramUrlInfoblox = busquedaInfoBlox + '&_return_fields=name,ipv4addrs&_max_results=10000'
    urlInfoblox = "'" + "https://172.31.169.82/wapi/v2.1/record:host?" + tipoBusqueda +"~=" + paramUrlInfoblox + "'"
    
    comandoGetValues = 'curl --fail --silent --show-error -u ' + userInfoBlox + ':' + passwordInfoBlox + ' --location -X GET -k1 ' + urlInfoblox  

    return comandoGetValues


def ejecutarComando(client, comando):
    output = ''
    hostBusqueda = []
    comandoParseo = ".[]|.name,.ipv4addrs[].ipv4addr"


    try:
        stdin, stdout, stderr = client.exec_command(comando)
        output = stdout.read().decode()
        err = stderr.read().decode()
        if err:
            print(err)
    except:
        print('Error al ejecutar el comando')

    try:
 
        hostBusqueda = list(jq.iter(comandoParseo, text=output))
        
    except:
        print('Error en el parseo json')

    return hostBusqueda



def conexionSSH():
    linky_user = validarVariableEntorno('linky_user')
    linky_pivot = validarVariableEntorno('linky_pivot')
    client = paramiko.SSHClient()
    client.set_missing_host_key_policy(paramiko.AutoAddPolicy())
    try:
        client.connect(hostname=linky_pivot, username=linky_user)

    except:
        print("[!] Cannot connect to the SSH Server")
        return None

   
    return client


def conectarInfoBlox(busquedaInfoBlox):
    arrayBusquedaInfoBlox = []
    
    if busquedaInfoBlox == '/file':
        busquedaFile = './search.lsl'
        try:
            file = open(busquedaFile, 'r')
            for line in file:
                if len(line.strip()) > 1:
                    arrayBusquedaInfoBlox.append(line)
        except:
            print('El archivo de busqueda search.lsl no se encuentra en la carpeta desde donde se ejecuta la aplicacion')  
            exit()  
    else:
        arrayBusquedaInfoBlox = busquedaInfoBlox.split(',')

    return procesarInfoBlox(arrayBusquedaInfoBlox)


def procesarInfoBlox(arrayBusquedaInfoBlox):

    eliminarArchivosHost()

    print("Consultando InfoBlox ....\n")
    client = conexionSSH()
    count = 0
    if client != None:
        ipHost = ''
        nameHost = ''
        hostFull = ''
        jerarquia = ''
        countNoRegistrados = 0 
        for busquedaInfoBlox in arrayBusquedaInfoBlox:
           
            comando = armarComando(busquedaInfoBlox.strip()) 
            hostBusqueda = ejecutarComando(client,comando)  
            countRegistros = 0 
            
            if len(hostBusqueda) > 0:
                for host in hostBusqueda:
                    if count % 2  == 0:
                        nameHost = host
                    else:
                        ipHost = host

                    if count % 2 != 0:
                        jerarquia = generarJerarquia(nameHost)
                        hostFull += ipHost + ';' + nameHost + ';' + jerarquia + '\n'            

                    count = count + 1
                    countRegistros = countRegistros + 1
            else:
                if is_valid_IP(busquedaInfoBlox):
                    hostFull += busquedaInfoBlox.strip() + ';' + busquedaInfoBlox.strip() + ';infoblox;nodata;nohost;nook\n' 
                    countNoRegistrados = countNoRegistrados + 1
                

            print ('Registros obtenidos : ' + busquedaInfoBlox.strip() + ' (' + str(int(countRegistros /2))  + ')')

        print( 'Total de registros obtenidos de infoblox  : ' + str(int(count /2)))
        if countNoRegistrados > 0:
            print ('Total de registros sin informacion en infoblox: ' + ' (' + str(countNoRegistrados)  + ')')

        hostFile = open('host.lhl', 'w')
        hostFile.write(hostFull)
        hostFile.close()    
        os.chmod('host.lhl',0o777)

    return (count / 2) + countNoRegistrados







def conectarHost(host, tipoDir):

    conectarInfoBlox(host)
    directorio = cargarArchivosHost()
    for fichero in directorio:    
        ips = find_host(fichero,host,tipoDir)
        if len(ips) == 1:
            conectar(ips[0])
        if len(ips) > 1:
            if ips.count(ips[0]) == len(ips):
                conectar(ips[0])
            else:
                print('Existe mas de una coincidencia para la conexion, realice una busqueda mas acotada ')
            
        


def buscarHost(host):

    conectarInfoBlox(host)
    directorio = cargarArchivosHost()

    for fichero in directorio:
        ip = find_host(fichero,host,'all')



def loadFiles(tipoOrden):
    path = cargarArchivosHost()
    
    findHost = [] 
    for filePath in path:
        numLinePath = 0
        file = open(filePath, 'r')
        for line in file:
            numLinePath = numLinePath + 1
            host_array = line.split(';')
            if len(host_array) != 6 and len(line) > 1:
                print('Error de formato en la linea ' + str(numLinePath) + ' en el archivo ' + str(filePath))

            if len(host_array) == 6:
                lhost_ip = host_array [0]
                lhost_name = host_array [1]
                lfolder_root = host_array [2]
                lfolder_group = host_array [3]
                lfolder_subgroup = host_array [4]

                ldatosHost = {'FILE' : str(filePath), 'LINE' : str(numLinePath), 'IP' : lhost_ip, 'HOSTNAME' :lhost_name, 'FOLDER_ROOT' :lfolder_root, 'FOLDER_GROUP' :lfolder_group, 'FOLDER_SUBGROUP' :lfolder_subgroup}
                findHost.append(ldatosHost)

    
    if tipoOrden == 'ip':
        findHost.sort(key=lambda x: x.get('IP'))
    
    if tipoOrden == 'tree':
        findHost.sort(key=lambda x: (x.get('FOLDER_ROOT'),x.get('FOLDER_GROUP'),x.get('FOLDER_SUBGROUP')))
       
    
    return findHost


def checkFiles(host):
    conectarInfoBlox(host)
    listaHostOrigen = loadFiles('ip')

    isOK = True
    listadoIP = dict(Counter(sub['IP'] for sub in listaHostOrigen))
    for listado in listadoIP:
        listIP = listado
        listCount = listadoIP[listado]
        if listCount > 1:
            print(end='\n')
        
        for listaOrigen in listaHostOrigen:
            if listIP == listaOrigen['IP'] and listCount > 1:
                print('IP duplicada : File ( ' + listaOrigen['FILE'] + ' ) | Line ( ' +  listaOrigen['LINE']  + ' ) | Ip ( ' + listaOrigen['IP']  + ' ) | HostName ( ' +  listaOrigen['HOSTNAME']  + ' ) ')
                isOK = False

    if isOK:
        print ('Archivos de Host sin problemas')

def treeFiles(busquedaInfoBlox):
    totalRegInfoBlox = conectarInfoBlox(busquedaInfoBlox)
    listaHostOrigen = loadFiles('tree')
    listJoinTree = []
    message = ''
      
    countRegistrosProcesados = 0

    listaHostOriginal = listaHostOrigen.copy()
    for listaHost2 in listaHostOriginal:         
        count = 0            
        for listaHost in listaHostOrigen:
            if listaHost['FOLDER_ROOT'] == listaHost2['FOLDER_ROOT'] and listaHost['FOLDER_GROUP'] == listaHost2['FOLDER_GROUP'] and listaHost['FOLDER_SUBGROUP'] == listaHost2['FOLDER_SUBGROUP']:
     
                listRoot = listaHost['FOLDER_ROOT']
                listGroup = listaHost['FOLDER_GROUP'] 
                listSubGroup = listaHost['FOLDER_SUBGROUP'] 
                joinTree = (listRoot + '/' + listGroup + '/' + listSubGroup)
                listJoinTree.append(joinTree)
                valorDuplicado = False
                for elem in listJoinTree:
                    if listJoinTree.count(elem) > 1:
                        valorDuplicado = True

                if not valorDuplicado:
                    print(end='\n')
                    message += '\n'
                    print(end='\n')
                    message += '\n' 
                    print (listRoot)
                    message += listRoot + '\n'
                    print ('|')
                    message += '|\n'                           
                    print ('|_____' + listGroup)
                    message += '|_____' + listGroup + '\n'
                    print ('      |')
                    message += '      |\n'
                    print ('      |_____' + listSubGroup)
                    message += '      |_____' + listSubGroup + '\n'

                else:
                    listJoinTree.remove(joinTree)

                print ('            |')
                message += '            |\n'
                print ('            |_____' + listaHost['IP'] + ' ( ' +  listaHost['HOSTNAME']  + ' )' )
                message += '            |_____' + listaHost['IP'] + ' ( ' +  listaHost['HOSTNAME']  + ' )\n' 
                countRegistrosProcesados = countRegistrosProcesados + 1     
                listaHostOrigen.pop(count)    
            count = count + 1   
                        
    treeFile = open('tree.lhosts', 'w')
    treeFile.write(message)
    treeFile.close()    
    os.chmod('tree.lhosts',0o777)
    print ('Registros generados en el arbol : ' + str(countRegistrosProcesados))
    print ('Archivo creado : ' + 'tree.lhosts')






def findJerarquia(searchRoot, searchGroup, searchSubGroup):

    listaHostOrigen = loadFiles('tree')
    listaHostDestino = []
    for listaHost in listaHostOrigen:
        if searchRoot != '' and searchGroup  != '' and searchSubGroup != '':
            if listaHost['FOLDER_ROOT'].find(searchRoot) > -1 and listaHost['FOLDER_GROUP'].find(searchGroup) > -1 and listaHost['FOLDER_SUBGROUP'].find(searchSubGroup) > -1:
                listaHostDestino.append(listaHost) 
        else:
            if searchRoot != '' and searchGroup  != '':
                if listaHost['FOLDER_ROOT'].find(searchRoot) > -1 and listaHost['FOLDER_GROUP'].find(searchGroup) > -1:
                    listaHostDestino.append(listaHost) 
            else:
                if searchRoot != '':
                    if listaHost['FOLDER_ROOT'].find(searchRoot) > -1:
                        
                        listaHostDestino.append(listaHost) 
    
    return listaHostDestino
            


def replaceNumber (cadena):
    K = 'x'
    # loop for all characters
    for ele in cadena:
        if ele.isdigit():
            cadena = cadena.replace(ele, K)

    
    cadena = replaceCaracter(cadena)
    return cadena




def replaceCaracter (cadena):
    K = '_'
    # loop for all characters
    for ele in cadena:
        if ele == '-':
            cadena = cadena.replace(ele, K)
    return cadena




def replaceCaracterInvalido (cadena):
    K = 'x'
    # loop for all characters

    
    for ele in cadena:
        if ele == '*':
            cadena = cadena.replace(ele, K)
        
    
    #if is_valid_IP(cadena):
    #    cadena = cadena + K    

    return cadena






def revisarDuplicado(listJoinCadena, strCadena):
    
    countCadena = ''
    numDuplicados = listJoinCadena.count(strCadena)       
    if numDuplicados > 1:
        numDuplicados = numDuplicados - 1
        countCadena = '_' + str(numDuplicados)
    return countCadena     



def ansibleFiles(busqueda,paramJerarquia):



    totalRegInfoBlox = int(conectarInfoBlox(busqueda))


    paramList = paramJerarquia.split(',')
    paramRoot = ''
    paramGroup = ''
    paramSubGroup = ''

    if len(paramList) == 1:
        paramRoot = paramList[0].strip()

    if len(paramList) == 2:
        paramRoot = paramList[0].strip()
        paramGroup = paramList[1].strip()
    
    if len(paramList) == 3:
        paramRoot = paramList[0].strip()
        paramGroup = paramList[1].strip()
        paramSubGroup = paramList[2].strip()

    
    

    if len(paramList) == 1 and paramRoot == 'all':
        listaHostOrigen = loadFiles('tree')
    else:
        listaHostOrigen = findJerarquia(paramRoot, paramGroup, paramSubGroup)

    listJoinTreeFull = []
    listJoinTreeRoot = []
    listJoinTreeGroup = []


    listJoinRoot = []
    listJoinGroup = []
    listJoinSubGroup = []
    listJoinHostName = []







    countRegistrosProcesados = 0

    if len(listaHostOrigen) > 0:
        message = 'all:\n   children:    '
    else:
        message = ''

    
    bar1 = Bar('Procesando:', max=totalRegInfoBlox)
    

    arrayJoinRoot = dict(Counter(sub['FOLDER_ROOT'] for sub in listaHostOrigen))
    arrayJoinGroup = dict(Counter(sub['FOLDER_GROUP'] for sub in listaHostOrigen))
    arrayJoinSubGroup = dict(Counter(sub['FOLDER_SUBGROUP'] for sub in listaHostOrigen))



    listaHostOriginal = listaHostOrigen.copy()
    for listaHost2 in listaHostOriginal:         
        count = 0
        for listaHost in listaHostOrigen:
            
                        

            if listaHost['FOLDER_ROOT'] == listaHost2['FOLDER_ROOT'] and listaHost['FOLDER_GROUP'] == listaHost2['FOLDER_GROUP'] and listaHost['FOLDER_SUBGROUP'] == listaHost2['FOLDER_SUBGROUP']:

                #if listaHost['FOLDER_ROOT'] == listaHost['FOLDER_GROUP'] or listaHost['FOLDER_ROOT'] == listaHost['FOLDER_SUBGROUP']  or listaHost['FOLDER_GROUP'] == listaHost['FOLDER_SUBGROUP']: 
                    #print (listaHost)



                listRoot = listaHost['FOLDER_ROOT']
                listGroup = listaHost['FOLDER_GROUP'] 
                listSubGroup = listaHost['FOLDER_SUBGROUP'] 

                joinTreeFull = (listRoot + '/' + listGroup + '/' + listSubGroup)
                listJoinTreeFull.append(joinTreeFull)
                jerarquiaFull = False
                
                for full in listJoinTreeFull:
                    if listJoinTreeFull.count(full) > 1:
                        jerarquiaFull = True
                        break

                if not jerarquiaFull: 
                    jerarquiaRoot = False
                    listJoinTreeRoot.append(listRoot)
                    for root in listJoinTreeRoot:
                        if listJoinTreeRoot.count(root) > 1:
                            jerarquiaRoot = True
                            break
                    
                    #########################################################################################################
                    listJoinRoot.append(replaceNumber(listRoot))
                    rootAnalizado = replaceNumber(listRoot) + revisarDuplicado(listJoinRoot,replaceNumber(listRoot))

                    listJoinGroup.append(replaceNumber(listGroup))
                    groupAnalizado = replaceNumber(listGroup) + revisarDuplicado(listJoinGroup,replaceNumber(listGroup))

                    listJoinSubGroup.append(replaceNumber(listSubGroup))
                    subGroupAnalizado = replaceNumber(listSubGroup) + revisarDuplicado(listJoinSubGroup,replaceNumber(listSubGroup)) 


                    if arrayJoinRoot.get(rootAnalizado,'empty') != 'empty': 
                        rootAnalizado = rootAnalizado + str(random.randint(0, 1000))

                    if arrayJoinGroup.get(groupAnalizado,'empty') != 'empty':
                        groupAnalizado = groupAnalizado + str(random.randint(0, 1000))

                    if arrayJoinSubGroup.get(subGroupAnalizado,'empty') != 'empty':
                        subGroupAnalizado = subGroupAnalizado + str(random.randint(0, 1000))

                    if arrayJoinRoot.get(groupAnalizado,'empty') != 'empty':
                        groupAnalizado = groupAnalizado + str(random.randint(0, 1000))

                    if arrayJoinRoot.get(subGroupAnalizado,'empty') != 'empty':
                        subGroupAnalizado = subGroupAnalizado + str(random.randint(0, 1000))

                    if arrayJoinGroup.get(subGroupAnalizado,'empty') != 'empty':
                        subGroupAnalizado = subGroupAnalizado + str(random.randint(0, 1000))

                    if (rootAnalizado ==  groupAnalizado):
                        groupAnalizado = groupAnalizado + str(random.randint(0, 1000))

                    if (rootAnalizado ==  subGroupAnalizado):
                        subGroupAnalizado = subGroupAnalizado + str(random.randint(0, 1000))

                    if (groupAnalizado ==  subGroupAnalizado):
                        subGroupAnalizado = subGroupAnalizado + str(random.randint(0, 1000))


                    #########################################################################################################
                    
                    saltoLinea = '\n                     '
                    hostsSection = saltoLinea + 'hosts:' + saltoLinea + '   '
                    if not jerarquiaRoot:                                        
                        message += '\n      ' + rootAnalizado + ': \n         children: \n            ' +  groupAnalizado + ': \n               children: \n                  ' + subGroupAnalizado + ':' + hostsSection                             
                    else:

                        jerarquiaGroup = False
                        listJoinTreeGroup.append(listGroup)
                        for group in listJoinTreeGroup:
                            if listJoinTreeGroup.count(group) > 1:
                                jerarquiaGroup = True
                                break

                        if not jerarquiaGroup: 
                            message += '\n            ' + groupAnalizado + ': \n               children: \n                  ' + subGroupAnalizado + ':' + hostsSection                 
                            
                        else:
                            message += '\n                  '  + subGroupAnalizado + ':' + hostsSection
                        listJoinTreeRoot.remove(listRoot)
                else:
                    listJoinTreeFull.remove(joinTreeFull) 


                #########################################################

                hostName = listaHost['HOSTNAME']
                #print(str(listJoinRoot.count(hostName)) + ' ' + str(listJoinGroup.count(hostName)) + ' ' + str(listJoinSubGroup.count(hostName)))
                
            
                
                
                if arrayJoinRoot.get(hostName,'empty') != 'empty' or arrayJoinGroup.get(hostName,'empty') != 'empty' or arrayJoinSubGroup.get(hostName,'empty') != 'empty': 
                    hostName = hostName + str(random.randint(0, 1000))

                listJoinHostName.append(hostName)
                hostAnalizado = replaceCaracterInvalido(hostName) + revisarDuplicado(listJoinHostName,hostName)

                #########################################################


                message +=hostAnalizado + ':\n                           ansible_host: ' +  listaHost['IP'] + saltoLinea + '   '
                countRegistrosProcesados = countRegistrosProcesados + 1
                listaHostOrigen.pop(count)
                bar1.next()
            count = count + 1


    bar1.finish()

    if message != '':                  
        ansibleFile = open( paramRoot + '.yml', 'w')
        ansibleFile.write(message)
        ansibleFile.close()    
        os.chmod(paramRoot + '.yml',0o777)
        print ('Registros generados en el inventario : ' + str(countRegistrosProcesados))
        print ('Archivo creado : ' + paramRoot + '.yml')
    
    else:

        print('¡¡ No existen patrones para la generacion de archivos ansible !!')









parser = argparse.ArgumentParser()
parser.add_argument("--info", help="Antes de conectarse deben cargar las siguientes variable de entorno: linky_user, linky_password, linky_pivot" )
parser.add_argument("-i", "--ip", help="  Conectarse a un host a traves de una ip o nombre de host",)
parser.add_argument("-f", "--find", help="  Buscar un host a traves de ip o hostname")
parser.add_argument("-c", "--check", help="  Verificar inconsistencias en archivos de host")
parser.add_argument("-a", "--ansible", help="  Generar inventarios de ansible")
parser.add_argument("-t", "--tree", help="  Mostrar arbol de host")

args = parser.parse_args()

# Aquí procesamos lo que se tiene que hacer con cada argumento
if args.info:
    print ('depuración activada!!!')

if args.ip:
    print ('Conexion a traves de ip!!!')
    conectarHost(args.ip,'all')


if args.find:
    print ('Busqueda de host!!!')
    buscarHost(args.find)

if args.check:
    print ('Check de archivos de host!!!')
    checkFiles(args.check)

if args.ansible:
    print ('Generacion de inventarios de ansible!!!')

    ansibleFiles(args.ansible, 'all')

if args.tree:
    print ('Arbol de host!!!')
    treeFiles(args.tree)






















