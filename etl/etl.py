import pandas as pd

def extract(input_csv: str) -> pd.DataFrame:
    try:
        # First try with semicolon separator
        df = pd.read_csv(input_csv, sep=";", engine="python")
        print(f"✅ CSV loaded with ';' separator - Shape: {df.shape}")
    except Exception as e1:
        try:
            # Fallback to comma separator
            df = pd.read_csv(input_csv, sep=",", engine="python")
            print(f"✅ CSV loaded with ',' separator - Shape: {df.shape}")
        except Exception as e2:
            # Final fallback to auto-detection
            df = pd.read_csv(input_csv, engine="python")
            print(f"✅ CSV loaded with auto-detection - Shape: {df.shape}")
    
    print(f"Columns found: {list(df.columns)}")
    return df

def normalize_colname(col: str) -> str:
    c = col.strip().lower()
    for ch in [' ', '-', '/', '(', ')', '.']:
        c = c.replace(ch, '_')
    return "_".join([p for p in c.split('_') if p != ""])

def get_experience_range_tuple(yoe):
    if pd.isna(yoe): return None
    try:
        y = float(yoe)
    except:
        return None
    if y < 1: return ("0-1", 0, 1)
    if y < 3: return ("1-3", 1, 3)
    if y < 5: return ("3-5", 3, 5)
    if y < 8: return ("5-8", 5, 8)
    return ("8+", 8, None)

def transform(df: pd.DataFrame) -> dict:
    df.columns = [normalize_colname(c) for c in df.columns]

    # Dates
    df['application_date_parsed'] = pd.to_datetime(df.get('application_date'), errors="coerce")
    if df['application_date_parsed'].isna().mean() > 0.1:
        df['application_date_parsed'] = pd.to_datetime(df.get('application_date'), errors="coerce", dayfirst=True)

    # Numeric
    for col in ['code_challenge_score', 'technical_interview_score', 'yoe']:
        if col in df.columns:
            df[col] = pd.to_numeric(df[col], errors="coerce")

    # Hired flag
    df['hired_flag'] = ((df.get('code_challenge_score', 0) >= 7) &
                        (df.get('technical_interview_score', 0) >= 7)).astype(int)

    # Candidate - Ensure unique keys
    fallback_series = pd.Series(['missing_email_' + str(i) for i in df.index], index=df.index)
    df['email_filled'] = df.get('email').fillna(fallback_series)
    
    # Create unique candidate_key based on email
    unique_emails = df['email_filled'].drop_duplicates().reset_index(drop=True)
    email_to_key = {email: idx + 1 for idx, email in enumerate(unique_emails)}
    df['candidate_key'] = df['email_filled'].map(email_to_key)
    
    # Create dimension table with unique candidates only
    dim_candidate = df[['candidate_key','email','first_name','last_name']].drop_duplicates().rename(columns={"yoe": "exactyoe"}).reset_index(drop=True)

    # Date - Use incremental keys instead of date strings
    date_df = df[['application_date_parsed']].drop_duplicates().dropna().reset_index(drop=True)
    date_df['date'] = date_df['application_date_parsed'].dt.date
    date_df['date_key'] = range(1, len(date_df) + 1)  # Incremental keys: 1, 2, 3, ...
    date_df['day'] = date_df['application_date_parsed'].dt.day
    date_df['month'] = date_df['application_date_parsed'].dt.month
    date_df['year'] = date_df['application_date_parsed'].dt.year
    dim_date = date_df[['date_key','date','day','month','year']]

    # Country - Ensure unique keys
    dim_country = pd.DataFrame(columns=['country_key','country_name'])
    if 'country' in df.columns:
        unique_countries = df['country'].dropna().drop_duplicates().reset_index(drop=True)
        dim_country = pd.DataFrame({
            'country_key': range(1, len(unique_countries) + 1),
            'country_name': unique_countries
        })

    # Seniority - Ensure unique keys
    dim_seniority = pd.DataFrame(columns=['seniority_key','seniority_name'])
    if 'seniority' in df.columns:
        unique_seniority = df['seniority'].dropna().drop_duplicates().reset_index(drop=True)
        dim_seniority = pd.DataFrame({
            'seniority_key': range(1, len(unique_seniority) + 1),
            'seniority_name': unique_seniority
        })

    # Technology - Ensure unique keys
    dim_technology = pd.DataFrame(columns=['technology_key','technology_name'])
    if 'technology' in df.columns:
        unique_technology = df['technology'].dropna().drop_duplicates().reset_index(drop=True)
        dim_technology = pd.DataFrame({
            'technology_key': range(1, len(unique_technology) + 1),
            'technology_name': unique_technology
        })

    # Experience Range
    df['experience_tuple'] = df['yoe'].apply(get_experience_range_tuple)
    exp_list = [t for t in df['experience_tuple'].dropna().unique()]
    dim_exp = pd.DataFrame(columns=['experience_key','range_label','min_years','max_years'])
    if exp_list:
        dim_exp = pd.DataFrame(exp_list, columns=['range_label','min_years','max_years']).reset_index(drop=True)
        dim_exp['experience_key'] = range(1,len(dim_exp)+1)
        dim_exp = dim_exp[['experience_key','range_label','min_years','max_years']]

    # Maps
    date_map = dict(zip(dim_date['date'], dim_date['date_key']))
    df['date_key'] = df['application_date_parsed'].dt.date.map(date_map)
    country_map = dict(zip(dim_country['country_name'], dim_country['country_key'])) if not dim_country.empty else {}
    seniority_map = dict(zip(dim_seniority['seniority_name'], dim_seniority['seniority_key'])) if not dim_seniority.empty else {}
    tech_map = dict(zip(dim_technology['technology_name'], dim_technology['technology_key'])) if not dim_technology.empty else {}
    exp_map = dict(zip(dim_exp['range_label'], dim_exp['experience_key'])) if not dim_exp.empty else {}

    df['country_key'] = df.get('country').map(country_map) if 'country' in df.columns else None
    df['seniority_key'] = df.get('seniority').map(seniority_map) if 'seniority' in df.columns else None
    df['technology_key'] = df.get('technology').map(tech_map) if 'technology' in df.columns else None
    df['experience_key'] = df['experience_tuple'].apply(lambda t: exp_map.get(t[0]) if (t is not None) else None)

    # Fact
    fact_cols = ['candidate_key','date_key','country_key','seniority_key','technology_key','experience_key',
                 'code_challenge_score','technical_interview_score','hired_flag','yoe']
    fact_app = df[fact_cols].copy()

    return {
        "Dim_Candidate": dim_candidate,
        "Dim_Date": dim_date,
        "Dim_Country": dim_country,
        "Dim_Seniority": dim_seniority,
        "Dim_Technology": dim_technology,
        "Dim_ExperienceRange": dim_exp,
        "Fact_Application": fact_app
    }