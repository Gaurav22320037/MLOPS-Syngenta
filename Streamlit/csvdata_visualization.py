import streamlit as st
import pandas as pd
import altair as alt
from sklearn.linear_model import LinearRegression
import numpy as np

# Set the page title and layout
st.set_page_config(page_title="Enhanced CSV Data Visualizer", layout="wide")

# App title and description
st.title("📊 Enhanced Interactive CSV Data Visualizer")
st.write("Upload your CSV file to explore and visualize the data with various chart types, including multi-column visualizations.")

# Sidebar for user interaction
st.sidebar.header("User Options")
uploaded_file = st.sidebar.file_uploader("Upload your CSV file", type=["csv"])

if uploaded_file:
    try:
        # Read the uploaded CSV file
        df = pd.read_csv(uploaded_file)
        st.write("### Uploaded Data Preview")
        st.dataframe(df)

        # Preprocess columns (strip whitespace from headers)
        df.columns = df.columns.str.strip()

        # Reset index for Altair compatibility
        df.reset_index(inplace=True)

        # Identify numeric columns for visualizations
        numeric_columns = df.select_dtypes(include=['number']).columns.tolist()
        non_numeric_columns = df.select_dtypes(exclude=['number']).columns.tolist()

        if not numeric_columns:
            st.error("No numeric columns found for visualization.")
        else:
            # User selects chart type
            chart_type = st.sidebar.selectbox("Select Chart Type", [
                "Line Chart", 
                "Bar Chart", 
                "Histogram", 
                "Scatter Plot", 
                "Area Chart", 
                "Pie Chart (Single Column)", 
                "Stacked Bar Chart", 
                "Heatmap", 
                "Boxplot"
            ])

            # Data transformation options
            if st.sidebar.checkbox("Enable Data Transformation"):
                st.write("### Data Transformation Options")
                # Drop rows with missing values
                if st.checkbox("Drop missing values"):
                    df = df.dropna()
                    st.write("Dropped missing values. Updated DataFrame:")
                    st.dataframe(df)

                # Filter rows
                filter_col = st.selectbox("Select column to filter", df.columns)
                filter_val = st.text_input(f"Enter value to filter rows in {filter_col}")
                if st.button("Apply Filter"):
                    df = df[df[filter_col].astype(str) == filter_val]
                    st.write(f"Filtered rows where `{filter_col}` equals `{filter_val}`:")
                    st.dataframe(df)

            if chart_type in ["Line Chart", "Bar Chart", "Histogram", "Area Chart"]:
                selected_column = st.sidebar.selectbox("Select a column for visualization", numeric_columns)

                if chart_type == "Line Chart":
                    st.write(f"### Line Chart for {selected_column}")
                    line_chart = alt.Chart(df).mark_line().encode(
                        x=alt.X('index:Q', title="Index"),
                        y=alt.Y(selected_column, title=selected_column)
                    ).properties(width=800, height=400).interactive()
                    st.altair_chart(line_chart)

                elif chart_type == "Bar Chart":
                    st.write(f"### Bar Chart for {selected_column}")
                    bar_chart = alt.Chart(df).mark_bar().encode(
                        x=alt.X('index:Q', title="Index"),
                        y=alt.Y(selected_column, title=selected_column)
                    ).properties(width=800, height=400).interactive()
                    st.altair_chart(bar_chart)

                elif chart_type == "Histogram":
                    st.write(f"### Histogram for {selected_column}")
                    histogram = alt.Chart(df).mark_bar().encode(
                        x=alt.X(selected_column, bin=True, title=selected_column),
                        y='count()'
                    ).properties(width=800, height=400).interactive()
                    st.altair_chart(histogram)

                elif chart_type == "Area Chart":
                    st.write(f"### Area Chart for {selected_column}")
                    area_chart = alt.Chart(df).mark_area().encode(
                        x=alt.X('index:Q', title="Index"),
                        y=alt.Y(selected_column, title=selected_column)
                    ).properties(width=800, height=400).interactive()
                    st.altair_chart(area_chart)

            elif chart_type == "Scatter Plot":
                if len(numeric_columns) > 1:
                    x_col = st.sidebar.selectbox("Select X-axis column", numeric_columns)
                    y_col = st.sidebar.selectbox("Select Y-axis column", numeric_columns, index=1)
                    st.write(f"### Scatter Plot: {x_col} vs {y_col}")
                    scatter_plot = alt.Chart(df).mark_circle(size=60).encode(
                        x=alt.X(x_col, title=x_col),
                        y=alt.Y(y_col, title=y_col),
                        tooltip=[x_col, y_col]
                    ).properties(width=800, height=400).interactive()
                    st.altair_chart(scatter_plot)
                else:
                    st.error("Scatter Plot requires at least two numeric columns.")

            elif chart_type == "Pie Chart (Single Column)":
                if len(non_numeric_columns) > 0:
                    pie_col = st.sidebar.selectbox("Select a column for Pie Chart", non_numeric_columns)
                    pie_data = df[pie_col].value_counts().reset_index()
                    pie_data.columns = [pie_col, 'count']
                    pie_chart = alt.Chart(pie_data).mark_arc().encode(
                        theta=alt.Theta(field='count', type='quantitative'),
                        color=alt.Color(field=pie_col, type='nominal'),
                        tooltip=[pie_col, 'count']
                    ).properties(width=800, height=400)
                    st.write(f"### Pie Chart for {pie_col}")
                    st.altair_chart(pie_chart)
                else:
                    st.error("Pie Chart requires at least one non-numeric column.")

            elif chart_type == "Stacked Bar Chart":
                if len(numeric_columns) > 1:
                    x_col = st.sidebar.selectbox("Select X-axis column (categorical or numeric)", df.columns)
                    y_cols = st.sidebar.multiselect("Select columns for stacking (numeric)", numeric_columns)
                    if y_cols:
                        stacked_data = df.melt(id_vars=x_col, value_vars=y_cols, var_name='Category', value_name='Value')
                        stacked_bar_chart = alt.Chart(stacked_data).mark_bar().encode(
                            x=alt.X(x_col, title=x_col),
                            y=alt.Y('Value', title="Value"),
                            color='Category:N',
                            tooltip=['Category', 'Value']
                        ).properties(width=800, height=400).interactive()
                        st.write(f"### Stacked Bar Chart for {', '.join(y_cols)} by {x_col}")
                        st.altair_chart(stacked_bar_chart)
                    else:
                        st.error("Select at least one column for stacking.")
                else:
                    st.error("Stacked Bar Chart requires multiple numeric columns.")

            elif chart_type == "Heatmap":
                corr = df.corr()
                st.write("### Heatmap of Correlations")
                heatmap = alt.Chart(corr.reset_index().melt('index')).mark_rect().encode(
                    x='index:O',
                    y='variable:O',
                    color='value:Q',
                    tooltip=['index', 'variable', 'value']
                ).properties(width=800, height=400)
                st.altair_chart(heatmap)

            elif chart_type == "Boxplot":
                selected_column = st.sidebar.selectbox("Select a column for Boxplot", numeric_columns)
                st.write(f"### Boxplot for {selected_column}")
                boxplot = alt.Chart(df).mark_boxplot().encode(
                    y=alt.Y(selected_column, title=selected_column)
                ).properties(width=400, height=400)
                st.altair_chart(boxplot)

            # Machine Learning - Linear Regression
            if st.sidebar.checkbox("Apply Linear Regression"):
                st.write("### Linear Regression")
                target_col = st.selectbox("Select Target Column (Y)", numeric_columns)
                feature_col = st.selectbox("Select Feature Column (X)", [col for col in numeric_columns if col != target_col])

                X = df[feature_col].values.reshape(-1, 1)
                y = df[target_col].values
                model = LinearRegression().fit(X, y)

                st.write(f"Model Coefficients: {model.coef_}")
                st.write(f"Intercept: {model.intercept_}")

                # Add regression line to scatter plot
                regression_chart = alt.Chart(df).mark_point().encode(
                    x=alt.X(feature_col, title=feature_col),
                    y=alt.Y(target_col, title=target_col)
                ) + alt.Chart(pd.DataFrame({
                    feature_col: df[feature_col],
                    target_col: model.predict(X)
                })).mark_line(color='red').encode(
                    x=feature_col,
                    y=target_col
                )
                st.altair_chart(regression_chart)

            # Download the processed data
            if st.sidebar.button("Download Processed Data"):
                csv = df.to_csv(index=False).encode('utf-8')
                st.download_button(
                    label="Download CSV",
                    data=csv,
                    file_name='processed_data.csv',
                    mime='text/csv',
                )

    except Exception as e:
        st.error(f"Error loading or processing the file: {e}")
else:
    st.info("Awaiting CSV file upload. Please upload a CSV file to proceed.")

# Footer
st.sidebar.markdown("---")

