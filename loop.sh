for animation in pulse cylon rainbow bargraph fill #midward 
do
	echo ${animation}
  for i in 10 20 30 40 50 60 70 80 90 100 
  do
    r=$(( (( RANDOM % 254 ) + 1 ) * ( RANDOM % 2 ) ))
    g=$(( (( RANDOM % 254 ) + 1 ) * ( RANDOM % 2 ) ))
    b=$(( (( RANDOM % 254 ) + 1 ) * ( RANDOM % 2 ) ))
    w=$(( (( RANDOM % 254 ) + 1 ) * ( RANDOM % 2 ) ))
    r2=$(( (( RANDOM % 254 ) + 1 ) * ( RANDOM % 2 ) ))
    g2=$(( (( RANDOM % 254 ) + 1 ) * ( RANDOM % 2 ) ))
    b2=$(( (( RANDOM % 254 ) + 1 ) * ( RANDOM % 2 ) ))
    w2=$(( (( RANDOM % 254 ) + 1 ) * ( RANDOM % 2 ) ))
    velocity=$(( (( RANDOM % 100 ) + 1 ) ))
    percent=$(( (( RANDOM % 100 ) + 1 ) ))
    set -x
    curl -i -X PUT -d "{\"animation\": \"${animation}\", \"rgbw2\": \"${r},${g},${b},${w}\", \"rgbw\": \"${r2},${g2},${b2},${w2}\", \"percent\": ${percent}, \"velocity\" : ${velocity}, \"bright\": 10}" localhost:9000/lumen && echo ""
    set +x
    sleep 2 
  done
done
