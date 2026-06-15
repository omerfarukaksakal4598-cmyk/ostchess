import streamlit as st
import chess

st.set_page_config(page_title="OST CHESS", layout="centered")

board = chess.Board()

if "selected" not in st.session_state:
    st.session_state.selected = None

st.title("♟️ OST CHESS")

# ---------------- PIECES IMAGES ----------------
piece_img = {
    "P": "assets/pieces/wp.png",
    "R": "assets/pieces/wr.png",
    "N": "assets/pieces/wn.png",
    "B": "assets/pieces/wb.png",
    "Q": "assets/pieces/wq.png",
    "K": "assets/pieces/wk.png",
    "p": "assets/pieces/bp.png",
    "r": "assets/pieces/br.png",
    "n": "assets/pieces/bn.png",
    "b": "assets/pieces/bb.png",
    "q": "assets/pieces/bq.png",
    "k": "assets/pieces/bk.png",
}

files = ["a","b","c","d","e","f","g","h"]

def sq_name(r,c):
    return chess.parse_square(files[c] + str(8-r))

# ---------------- BOARD ----------------
for r in range(8):
    cols = st.columns(8)

    for c in range(8):
        sq = sq_name(r,c)
        piece = board.piece_at(sq)

        img = None

        if piece:
            img = piece_img[piece.symbol()]

        if cols[c].button(" ", key=str(r)+str(c)):
            
            if st.session_state.selected is None:
                if piece:
                    st.session_state.selected = sq
            else:
                move = chess.Move(st.session_state.selected, sq)

                if move in board.legal_moves:
                    board.push(move)

                st.session_state.selected = None

        if img:
            cols[c].image(img, width=60)

# ---------------- INFO ----------------
st.write("Turn:", "White" if board.turn else "Black")

if board.is_check():
    st.error("CHECK!")

if board.is_checkmate():
    st.error("CHECKMATE!")
