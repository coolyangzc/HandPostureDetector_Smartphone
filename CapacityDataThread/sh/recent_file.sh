IFS=$'\n'                    
output=(`ls -l`)            
lines=${#output[@]}          
echo ${output[$((lines-1))]} 