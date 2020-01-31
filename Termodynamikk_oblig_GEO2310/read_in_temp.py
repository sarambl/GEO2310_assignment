import pandas as pd
def read_temperatures_and_interpolate_to_grid(filename, p_mid):
	test=pd.read_csv(filename,index_col=0)
	test=test.rename(columns={'press': 'p_mid'})
	grid_df = pd.DataFrame({'p_mid':p_mid})
	#grid_df.index.name = 'z_mid'
	#grid_df['p_mid']=grid.p_mid

    #grid_df=grid.data
    #print(grid_df)
	out = test.merge(grid_df,on='p_mid', how='outer').set_index('p_mid').sort_index(ascending=True).interpolate(limit_direction='backward').merge(grid_df,on='p_mid', how='inner')
	return out['temp'].values[::-1]
