import asyncio
import json
from random import randint
import sys
import websockets
import time


async def send(websocket, action, data):
    message = json.dumps(
        {
            'action': action,
            'data': data,
        }
    )
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
            print('aca viene todo----------------')
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
    turn_action = randint(0, 4)
    if turn_action > 0:
    # if turn_action > 1:
        await process_move(websocket, request_data)
    # elif turn_action == 0:
    #     await process_kill_col(websocket, request_data)
    else:
        await process_kill_row(websocket, request_data)


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

def is_valid_move(board, column):
    rows = len(board)
    if column < 0 or column >= len(board[0]):
        # La columna está fuera del rango del tablero
        return False
    for row in range(rows - 1, -1, -1):
        if board[row][column] == ' ':
            # La posición está vacía, el movimiento es válido
            return True
    # La columna está llena
    return False

async def process_move(websocket, request_data):
    side = request_data['data']['side']
    board = request_data['data']['board']
    columns = board.find('|', 1) - 1
    print(board)
    
    # Inicializar la columna como inválida
    column = None

    # Elegir una columna aleatoria hasta encontrar una válida
    while column is None or not is_valid_move(board, column):
        column = randint(0, columns - 1)
    
    # Enviar el movimiento al servidor del juego
    await send(
        websocket,
        'move',
        {
            'game_id': request_data['data']['game_id'],
            'turn_token': request_data['data']['turn_token'],
            'col': column,
        },
    )

if __name__ == '__main__':
    # if len(sys.argv) >= 2:
        auth_token = "eyJ0eXAiOiJKV1QiLCJhbGciOiJIUzI1NiJ9.eyJ1c2VyIjoidmNvbW1hdHRlb0BnbWFpbC5jb20ifQ.FL1Monl-6d6YJjMOsLYnDO7nzihYuP_Y1e2Pe_WcKOQ"
        # auth_token = sys.argv[1]
        asyncio.get_event_loop().run_until_complete(start(auth_token))
    # else:
      #  print('please provide your auth_token')
