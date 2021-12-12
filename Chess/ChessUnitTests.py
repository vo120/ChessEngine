from Chess.ChessEngine import GameBoard
import ChessMain
import unittest, mock
class CheckMoveValidity(unittest.TestCase):
    @mock.patch('ChessMain.isMoveValid')
    def test_MoveValid(self, mockisMoveValid):
        'Unit Test for isMoveValid method in ChessMain'
        gs = GameBoard(0)
        chess_game_obj = ChessMain()
        chess_game_obj.isMoveValid(gs.drawStateOfGame(), "black")

        expected_arg_calls = []
        for rows in range(0, 2):
            for colns in range(0, 8):
                expected_arg_calls.append(mock.call(gs.drawStateOfGame(), 'black', (rows, colns)))
        self.assertEqual(mockisMoveValid.call_args_list, expected_arg_calls)
if __name__=="__main__":
    unittest.main()

    '''
    This method will show if a king is in check or not. 
    '''


    #def isInCheck():
        #pass

    '''
    This method will show if a king is in checkmate or not
    '''


    #def isInCheckmate():
        #pass