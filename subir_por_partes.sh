# Agregar las subcarpetas de addons por separado
for subcarpeta in addons/*; do
    echo "Agregando y subiendo: $subcarpeta"
    git add "$subcarpeta/"
    git commit -m "Subiendo $subcarpeta"
    git push origin main
done
