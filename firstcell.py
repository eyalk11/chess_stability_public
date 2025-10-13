import chess
import ipywidgets as widgets
import chess.pgn
import numpy as np
import io
import sys
import nest_asyncio 
nest_asyncio.apply()

class Calculator:
    async def sendit(self,fen):
        from sendj import send_message,LAM 
        t= {'type':'MANUAL','fen':fen}
        return (await send_message( {"action":"sendmessage", "data": t } if LAM else t))

    
    def print_stats(self,b,turn):
        print(asyncio.run(self.async_ret_stats(b,turn)))
        
    async def async_ret_stats(self,b,turn):
        if turn!=b.turn:
            raise Exception("Turns doesnt match" )
        field='score','stability all','stability same','stability diff','moves by depth','analysis_time_seconds' 
        res= (await self.sendit(b.fen()))
        if not res:
            return 
        st=''
        for k in field:
            st+=  f"{k}: {res[k]}\n"
        try:
            for k in res['pv_analysis'][:3]:
                st+="%s stab same/diff: %s / %s\n" %(k['pv'], k['stability_same'],k['stability_diff'])
        except:
            pass
        return st
            
        
    
from ipywidgets import interact, interactive, fixed, interact_manual, SelectMultiple, Combobox, HBox, VBox
import ipywidgets as widgets
import chess.engine

from chess._interactive import InteractiveViewer
from IPython.display import clear_output
import asyncio
from random import randrange
gbuf=""

def get_game(pgn):
    p = chess.pgn.read_game(io.StringIO(pgn))
    gam = p.game()
    return gam


class GameDispCalc(InteractiveViewer):    

    @classmethod
    def create(cls,pgn):
        iv=get_game(pgn)._interactive_viewer()
        iv.__class__=cls
        iv.patch()
        return iv

    def patch(self):
        from copy import deepcopy
        gam= deepcopy(self.game)

        ls=[]
        for i,k in enumerate(self._InteractiveViewer__moves):
            san=gam.board().san(k)
            gam=gam.next()
            ls+=[san]
        self._InteractiveViewer__white_moves = [str(move) for (i, move) in enumerate(ls) if i % 2 == 0]
        self._InteractiveViewer__black_moves = [str(move) for (i, move) in enumerate(ls) if i % 2 == 1]
        self.moves=ls
        self.calc= Calculator( )
        self.task=None
        
        self.w= widgets.Output(layout={'border': '1px solid black'}) #widgets.interactive_output(f, {'a': 1, 'b': 2, 'c': 3})
    
    async def run_task(self,b):
        
        res = await self.calc.async_ret_stats(b,b.turn)

        
        nm=self._InteractiveViewer__next_move
        
        if nm>0:
            self.w.append_stdout(self.moves[nm-1])
        
        self.w.append_stdout('\n'+str(res))

        self.show(False)
        
    def show(self,fut=True):
        global gbuf
        clear_output(wait=True)
        
        InteractiveViewer.show(self)
        
        
        if self.task:
            self.task.cancel()
        b=self.game.board()
        loop = asyncio.get_event_loop()
        
        
        
        b=self._InteractiveViewer__board

        if fut:
            self.w= widgets.Output(layout={'border': '1px solid black'})
        with self._InteractiveViewer__out:
            display(self.w)

        if fut:
            self.task=asyncio.create_task(self.run_task(b))      
   
        
        
            
            
        
def display_game(pgn):
    iv= GameDispCalc.create(pgn)
    iv.show()
    return iv

def display_board(fen,iswhite=None,simp=False): #actually display fen 
    mycalc=Calculator()
    b=chess.Board(fen)
    if iswhite is None:
        iswhite= b.turn
    display( widgets.HTML(str(b._repr_svg_())))
    if not simp:
        mycalc.print_stats(b,iswhite)
    return mycalc
