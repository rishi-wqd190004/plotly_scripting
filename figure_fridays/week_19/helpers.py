def summary_metrics(df):
    '''
    acceptance rate, rejection rate, pending application and total applications'''
    total_apps = df['App No'].nunique()

    df_success = df[df["Status"] == 'Approved - License Issued']
    df_reject = df[df['Status'] == 'Denied']
    df_pending = df[(df['Status'] == 'Pending Fitness Interview')]
    df_incomplete = df[df['Status'].isin(['Incomplete'])]
    df_review = df[df['Status'].isin(['Under Review'])]

    success_cnt = df_success['App No'].nunique()
    reject_cnt = df_reject['App No'].nunique()
    pending_cnt = df_pending['App No'].nunique()
    incomplete_cnt = df_incomplete['App No'].nunique()
    review_cnt = df_review['App No'].nunique()

    acc_rate = (success_cnt / total_apps) * 100 if total_apps else 0
    reject_rate = (reject_cnt / total_apps) * 100 if total_apps else 0

    return {
        'acceptance_rate': round(acc_rate, 2),
        'rejection_rate': round(reject_rate, 2),
        'pending_applications': pending_cnt,
        'total_applications': total_apps,
        'incomplete_applications': incomplete_cnt,
        'under_review': review_cnt
    }
