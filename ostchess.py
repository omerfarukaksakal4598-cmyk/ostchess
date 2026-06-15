import streamlit as st
import chess

st.set_page_config(page_title="OST CHESS", layout="centered")

# ---------------- STATE ----------------
if "board" not in st.session_state:
    st.session_state.board = chess.Board()

if "selected" not in st.session_state:
    st.session_state.selected = None

board = st.session_state.board

# ---------------- TITLE ----------------
st.title("♟️ OST CHESS")

# ---------------- BOARD UI ----------------
files = ["a","b","c","d","e","f","g","h"]

def square_name(r, c):
    return chess.parse_square(files[c] + str(8 - r))

def render_board():
    cols = st.columns(8)

    for r in range(8):
        row_cols = st.columns(8)

        for c in range(8):
            sq = square_name(r, c)
            piece = board.piece_at(sq)

            color = "#EEEED2" if (r+c)%2==0 else "#769656"

            label = " "

            if piece:
                label = piece.symbol()

            if row_cols[c].button(label, key=str(r)+str(c)):
                
                # SELECTION LOGIC
                if st.session_state.selected is None:
                    if piece:
                        st.session_state.selected = sq
                else:
                    move = chess.Move(st.session_state.selected, sq)

                    if move in board.legal_moves:
                        board.push(move)

                    st.session_state.selected = None

render_board()

# ---------------- INFO ----------------
st.write("Turn:", "White" if board.turn else "Black")

if board.is_check():
    st.error("CHECK!")

if board.is_checkmate():
    st.error("CHECKMATE!")

# ---------------- RESET ----------------
if st.button("Reset Game"):
    st.session_state.board = chess.Board()
    st.session_state.selected = None
