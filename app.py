
import streamlit as st 
import pandas as pd 
import tabula 
import io
# from io import StringIO 
# import requests
from tempfile import NamedTemporaryFile

st.title('Estrai tabelle excel da un file in formato .pdf')

st.subheader('Questa è una versione beta') 


uploaded_file = st.file_uploader("Carica il tuo file", type = ['.pdf'])  

# ===> Check this, it might turn useful !!!! 
#temp_file = NamedTemporaryFile(delete=False)

#if 'file' not in st.session_state:
#	st.session_state.file = file

st.write('------')

col1, col2, col3 = st.columns(3)

with col1:
	pag_inizio = st.number_input('Inserisci inizio pagina', 
							 min_value = 1, max_value = 50, value = 1,
							 step = 1)
	pag_fine = st.number_input('Inserisci fine pagina',
		                     min_value = 1, max_value = 50, value = 1,
	                         step = 1)

with col2:
	opzione = st.radio('Seleziona una opzione', ['pulisci testo', 'stream di dati'])

with col3:
	senza_intestazione = st.checkbox('Senza intestazione')

#if opzioni == None or opzioni == 'pag_con_testo':
#	lattice == Tru

# Use only the testo as a condition and leave as a default the lattice = True

if opzione == 'stream di dati':
	lattice, stream_dati = False, True
else:
	lattice, stream_dati = True, False


header = None if senza_intestazione else 0 

print('header is', header)

if pag_inizio != pag_fine:
	num_pagine = list(range(pag_inizio, pag_fine+1))
else:
	num_pagine = pag_inizio


st.write('Num pagine', num_pagine)
print(num_pagine)
st.write('------')


if 'button' not in st.session_state:
	st.session_state.button = False  

st.session_state.button = st.button('Click per convertire file')

st.write('STATE Button', st.session_state.button)

# here we need to add the session_state

def extract_table(file,  pages, lattice, stream_dati, header):
	if header == 0:
		if type(pages) == int:
			df = tabula.read_pdf(file, pages = pages, lattice = lattice, stream = stream_dati)[0]
		elif len(pages) > 1:
			# for pagine multiple 
			df_ = tabula.read_pdf(file, pages = pages, lattice = lattice, stream = stream_dati)
			if len(df_) > 1:
				df = pd.concat([df_[i] for i in range(len(df_))])
                      		
                     		
	elif header == None:
		if type(pages) == int:
			df = tabula.read_pdf(file, pages = num_pagine, lattice = lattice, stream = stream_dati, 
							           pandas_options = {'header': header})[0]
		else:
			df_ = tabula.read_pdf(file, pages = pages, lattice = lattice, stream = stream_dati,
                                      pandas_options = {'header': header})
			if len(df_) > 1:
				df = pd.concat([ df_[i] for i in range(len(df_))])
                                 
	return df

if st.session_state.button:
	
	df = extract_table(uploaded_file, num_pagine, lattice, stream_dati, header)
		
	st.write('La lungezza del file è pari a', df.shape) 

	st.subheader('Visualizza la tabella estratta')
	
	if len(df) <= 20: 
		st.dataframe(df)
	else: 
		st.dataframe(df.head())
		st.dataframe(df.tail())

	buffer = io.BytesIO()
	#nome_file = st.text_input('Scrivi il nome del file da salvare')

	with pd.ExcelWriter(buffer, engine = 'xlsxwriter') as writer:
		# Write each dataframe to a different worksheet
		df.to_excel(writer, index = False)

		# Close the Pnadas excel writtter and ouput the Excel file to the wrapper 
		writer.save()
		
		# button = st.button('Clicca qui per scaricare il file', key = 'one')

# Could it have to do with download_button that removed all the state ????? 

	down_butt = st.download_button(
			    label = "Download data as CSV",
			    data = buffer,
			    #file_name = f'{nome_file}.xlsx',
			    file_name = 'nome_file.xlsx',
			    mime = "application/vnd.ms-excel",
			)
	if down_butt:
		st.success('Il suo file è stato scaricato correttamente. Per visualizzare il file cerca nella cartella Downloads del suo pc.')
