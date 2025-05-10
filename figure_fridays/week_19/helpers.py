def summary_metrics(df):
    '''
    acceptance rate, rejection rate, pending application and total applications'''
    total_apps = df['App No'].nunique()

    df_success = df[df["Status"] == 'Approved - License Issued']
    df_reject = df[df['Status'] == 'Denied']
    df_pending = df[df['Status'] == 'Pending Fitness Interview' or df["Status"] == 'Incomplete']

    acc_rate = (df_success / total_apps) * 100
    reject_rate = (df_reject / total_apps) * 100
    pending_cnt = df_pending.nunique()

    return {
        'acceptance_rate': round(acc_rate, 2),
        'rejection_rate': round(reject_rate, 2),
        'pending_rate': pending_cnt
    }
