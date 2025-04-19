import streamlit as st
import pandas as pd
import numpy as np
import matplotlib.pyplot as plt
from io import BytesIO

st.set_page_config(layout="wide")
st.title("🌐 Relationship Space Visualizer")

# Sidebar input for adding a new person
st.sidebar.header("Add New Relationship")
new_name = st.sidebar.text_input("Name")
give = st.sidebar.slider("Give", 0, 100, 50)
take = st.sidebar.slider("Take", 0, 100, 50)
hot = st.sidebar.slider("Hot", 0, 100, 50)
cold = st.sidebar.slider("Cold", 0, 100, 50)
n = st.sidebar.slider("Closeness (n)", 1, 10, 1)

# File uploader
st.sidebar.markdown("---")
uploaded_file = st.sidebar.file_uploader("Upload CSV file", type=["csv"])

# Initial data or session state
def initialize_data():
    return pd.DataFrame({
        'name': ['mum', 'dad', 'chris', 'Jum', 'Jom'],
        'give': [0, 0, 50, 40, 80],
        'take': [100, 100, 50, 60, 20],
        'hot': [70, 10, 70, 70, 50],
        'cold': [30, 90, 30, 30, 50],
        'n': [1, 1, 1, 1, 1]
    })

if 'df' not in st.session_state:
    st.session_state.df = initialize_data()

# Load uploaded data if available
if uploaded_file is not None:
    st.session_state.df = pd.read_csv(uploaded_file)

# Add new entry
if new_name:
    new_entry = pd.DataFrame([{
        'name': new_name,
        'give': give,
        'take': take,
        'hot': hot,
        'cold': cold,
        'n': n
    }])
    st.session_state.df = pd.concat([st.session_state.df, new_entry], ignore_index=True)

# Delete functionality
st.sidebar.markdown("---")
delete_name = st.sidebar.selectbox("Delete a name", ["None"] + list(st.session_state.df['name']))
if delete_name != "None":
    st.session_state.df = st.session_state.df[st.session_state.df['name'] != delete_name]

# AI-based suggestion
st.subheader("💡 Suggested Relationship Tags")
def suggest_relationship(row):
    if row['give'] > 70 and row['hot'] > 70:
        return "❤️ Warm Giver"
    elif row['take'] > 70 and row['cold'] > 70:
        return "❄️ Cold Taker"
    elif row['give'] == row['take']:
        return "⚖️ Balanced"
    else:
        return "🤝 Complex"

st.session_state.df['tag'] = st.session_state.df.apply(suggest_relationship, axis=1)

# Show raw data
st.subheader("📋 Relationship Data")
st.dataframe(st.session_state.df, use_container_width=True)

# Download link
csv = st.session_state.df.to_csv(index=False)
buffer = BytesIO()
buffer.write(csv.encode())
buffer.seek(0)
st.download_button("⬇️ Download Data as CSV", buffer, file_name="relationship_data.csv", mime="text/csv")

# Prepare data for visualization
df = st.session_state.df.copy()
df['x_pct'] = df['hot'] / (df['hot'] + df['cold']) * 100
df['y_pct'] = df['give'] / (df['give'] + df['take']) * 100
x_shifted = df['x_pct'] - 50
y_shifted = df['y_pct'] - 50
angles = np.arctan2(y_shifted, x_shifted)
x_pos = df['n'] * np.cos(angles)
y_pos = df['n'] * np.sin(angles)

# Create the visualization
fig, ax = plt.subplots(figsize=(6, 6))
ax.axhline(0, color='gray', linewidth=0.5)
ax.axvline(0, color='gray', linewidth=0.5)

max_radius = int(df['n'].max()) + 1
for r in range(1, max_radius):
    circle = plt.Circle((0, 0), r, color='lightgray', fill=False, linestyle='--', linewidth=0.5)
    ax.add_patch(circle)
    ax.text(0, r, f'n={r}', ha='center', va='bottom', fontsize=8, color='gray')

for i, row in df.iterrows():
    ax.scatter(x_pos[i], y_pos[i])
    label = f"{row['name']} {row['tag']}"
    ax.text(x_pos[i] + 0.1, y_pos[i] + 0.1, label, fontsize=9)

ax.scatter(0, 0, color='black', s=50, marker='*')
ax.text(0.2, 0.2, 'me', fontsize=10, weight='bold', color='black')
ax.set_title('Relationship Space')
ax.set_xlabel('Emotional Direction (%Hot)')
ax.set_ylabel('Relational Direction (%Give)')
ax.set_aspect('equal')
ax.grid(True)

# Display side-by-side with raw data
st.subheader("🗺️ Visual Relationship Map")
st.pyplot(fig)

# Footer note
st.markdown("---")
st.markdown("Made with 💛 by you & ChatGPT")
