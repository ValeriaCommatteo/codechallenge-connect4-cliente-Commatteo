import asyncio
import json
from random import randint
import sys
import websockets
import time
import random


async def send(websocket, action, data):
    message = json.dumps({'action': action,'data': data})
    print(message)
    await websocket.send(message)

async def start(auth_token):
    uri = "ws://codechallenge-server-f4118f8ea054.herokuapp.com/ws?token={}".format(auth_token)
    while True:
        try:
            print('connection to {}'.format(uri))
            async with websockets.connect(uri) as websocket:
                print('connection READY!')
                await play(websocket)
        except KeyboardInterrupt:
            print('Exiting...')
            break
        except Exception:
            print('connection error!')
            time.sleep(3)

async def play(websocket):
    while True:
        try:
            request = await websocket.recv()
            print(f"< {request}")
            request_data = json.loads(request)
            if request_data['event'] == 'update_user_list':
                pass
            if request_data['event'] == 'game_over':
                board = request_data['data']['board']
                print(board)
            if request_data['event'] == 'challenge':
                # if request_data['data']['opponent'] == 'favoriteopponent':
                await send(
                    websocket,
                    'accept_challenge',
                    {
                        'challenge_id': request_data['data']['challenge_id'],
                    },
                )
            if request_data['event'] == 'your_turn':
                await process_your_turn(websocket, request_data)
        except KeyboardInterrupt:
            print('Exiting...')
            break
        except Exception as e:
            print('error {}'.format(str(e)))
            break  # force login again

async def process_your_turn(websocket, request_data):
    turn_action = 1
    if turn_action == 1:
        await process_move(websocket, request_data)

async def process_kill_col(websocket, request_data):
    side = request_data['data']['side']
    board = request_data['data']['board']
    colums = board.find('|', 1) - 1
    print(board)
    await send(
        websocket,
        'kill',
        {
            'game_id': request_data['data']['game_id'],
            'turn_token': request_data['data']['turn_token'],
            'col': randint(0, colums),
        },
    )

async def process_kill_row(websocket, request_data):
    side = request_data['data']['side']
    board = request_data['data']['board']
    rows = board.count('\n')
    print(board)
    await send(
        websocket,
        'kill',
        {
            'game_id': request_data['data']['game_id'],
            'turn_token': request_data['data']['turn_token'],
            'row': randint(0, rows - 1),
        },
    )

# # Funcion para generar los posibles movimientos    
# def generate_moves(board, column):  # No funciona, no actualiza el listado y cuando se empieza a usar el kill no sabe que hacer.
#     valid_moves = [] # Creo una lista vacia para despues guardar los movimientos.
#     rows = board.count('\n')

#     for row in range(rows -1, -1, - 1):  # Itera sobre las filas en orden inverso, desde la penúltima fila hasta la primera fila.
#         if board.split('\n')[row][column] == ' ':
#             valid_moves.append(row)  # Si la posición está vacía, agrega la fila actual a la lista de movimientos válidos.

#     return valid_moves    

# Funcion para chequear los movimientos
def check_moves(board, column, player_symbol):
    print('entra al check')
    row = get_lowest_empty_row(board, column) # Obtener la fila más baja disponible en la columna
    if row is None:
        return False  # La columna está llena, no se puede hacer un movimiento aquí
    
    print('check')

    # Verificar movimiento es ganador en alguna dirección
    if check_horizontal(board, column, player_symbol):
        print('pasa horizontal')
        return True
    if check_vertical(board, column, player_symbol):
        print('pasa vertical')
        return True
    if check_diagonal(board, column, player_symbol):
        print('pasa diagonal')
        return True

    return False

def get_lowest_empty_row(board, column): # Funcion chequeada y funcionando.
    board = board.strip().split('\n')
    
    for row in range(len(board) - 1, -1, -1):
        trimmed_row = board[row].strip()
        if trimmed_row[column] == ' ':
            return row
    return None

# Funcion de secuencia ganadora horizontalmente
def check_horizontal(board, column, player_symbol): # Funcion chequeada y funcionando.
    board = board.strip().split('\n')
    rows = len(board)
    consecutive_count = 0

    for row in range(rows):
        for column in range(column):
            print('entra el segundo for')
            if board[row][column] == player_symbol:
                consecutive_count += 1

                if consecutive_count == 4:
                    return True
            else:
                consecutive_count = 0

        consecutive_count = 0  # Reiniciar el contador al cambiar de fila si no entra el if anterior x eso esta 2 veces.
    return False

def check_vertical(board, column, player_symbol): # Verificar si hay una secuencia ganadora verticalmente
    board = board.strip().split('\n')
    rows = len(board)
    count = 0

    for r in range(max(0, rows - 3), min(len(board), rows + 4)):
        if board[r][column] == player_symbol:
            count += 1
            if count == 4:
                return True
        else:
            count = 0
    return False

def check_diagonal(board, column, player_symbol): # Verificar si hay una secuencia ganadora en diagonal
    board = board.strip().split('\n')
    rows = len(board)
    for dr, dc in [(1, 1), (1, -1), (-1, 1), (-1, -1)]:
        count = 0
        for i in range(-3, 4):
            r = rows + i * dr
            c = column + i * dc
            if 0 <= r < len(board) and 0 <= c < len(board[0]) and board[r][c] == player_symbol:
                count += 1
                if count == 4:
                    return True
            else:
                count = 0
    return False

def is_valid_move(board, column):
    rows = board.count('\n')  # Cuenta las filas en el tablero

    for row in range(rows - 1, -1, -1):  # Iterar sobre las filas en orden inverso
        if board.split('\n')[row][column] == ' ':  # Verificar si la posición está vacía
            return True  # Se encontró al menos una posición vacía en la columna

    return False  # No se encontraron posiciones vacías en la columna

async def process_move(websocket, request_data):
    side = request_data['data']['side']
    board = request_data['data']['board']
    columns = board.find('|', 1) - 1
    rows = board.count('\n')
    player_symbol = 'S' if side == 'S' else 'N'

    # Elegir una columna aleatoria
    desired_column = randint(0, columns - 1)

     # Verificar si el movimiento es válido en la columna seleccionada
    if is_valid_move(board, desired_column):
        # Si el movimiento es válido, verificar si es un movimiento ganador
        if check_moves(board, desired_column, player_symbol):
            # Realizar el movimiento ganador
            await send(
                websocket,
                'move',
                {
                    'game_id': request_data['data']['game_id'],
                    'turn_token': request_data['data']['turn_token'],
                    'col': desired_column,
                },
            )
            return
            
        else:
            print(board)
            await send(
                websocket,
                'move',
                {
                    'game_id': request_data['data']['game_id'],
                    'turn_token': request_data['data']['turn_token'],
                    'col': desired_column,
                },
            )
    else:
        action = random.choice([process_kill_col, process_kill_row])
        await action(websocket, request_data)
    

if __name__ == '__main__':
    # if len(sys.argv) >= 2:
        auth_token = "eyJ0eXAiOiJKV1QiLCJhbGciOiJIUzI1NiJ9.eyJ1c2VyIjoidmNvbW1hdHRlb0BnbWFpbC5jb20ifQ.FL1Monl-6d6YJjMOsLYnDO7nzihYuP_Y1e2Pe_WcKOQ" # Haciendo esto no tengo que poner el token cada vez que quiera correr la terminal
        # auth_token = sys.argv[1]
        asyncio.get_event_loop().run_until_complete(start(auth_token))
    # else:
      #  print('please provide your auth_token')
