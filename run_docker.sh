#!/bin/bash

# Script para ejecutar la Plataforma de Créditos IA en Docker
# Uso: ./run_docker.sh [comando]

set -e

# Colores para output
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
BLUE='\033[0;34m'
NC='\033[0m' # No Color

# Función para imprimir mensajes coloreados
print_info() {
    echo -e "${BLUE}[INFO]${NC} $1"
}

print_success() {
    echo -e "${GREEN}[SUCCESS]${NC} $1"
}

print_warning() {
    echo -e "${YELLOW}[WARNING]${NC} $1"
}

print_error() {
    echo -e "${RED}[ERROR]${NC} $1"
}

# Verificar si Docker está instalado
check_docker() {
    if ! command -v docker &> /dev/null; then
        print_error "Docker no está instalado. Por favor instala Docker primero."
        exit 1
    fi

    if ! command -v docker-compose &> /dev/null; then
        print_error "Docker Compose no está instalado. Por favor instala Docker Compose primero."
        exit 1
    fi
}

# Verificar archivos necesarios
check_files() {
    if [ ! -f ".env" ]; then
        print_error "Archivo .env no encontrado. Copia .env.example a .env y configura tus variables."
        exit 1
    fi

    if [ ! -d "security" ]; then
        print_error "Directorio security/ no encontrado. Ejecuta 'python setup_security.py' primero."
        exit 1
    fi
}

# Construir imagen Docker
build_image() {
    print_info "Construyendo imagen Docker..."
    docker-compose build
    print_success "Imagen construida exitosamente"
}

# Ejecutar contenedor
run_container() {
    local command="${1:-python main.py test_data.json}"

    print_info "Ejecutando contenedor con comando: $command"
    docker-compose run --rm credit-agent $command
}

# Ejecutar en modo interactivo
run_interactive() {
    print_info "Ejecutando contenedor en modo interactivo..."
    docker-compose run --rm credit-agent bash
}

# Limpiar contenedores e imágenes
clean_docker() {
    print_warning "Limpiando contenedores e imágenes..."
    docker-compose down -v --rmi all 2>/dev/null || true
    docker system prune -f
    print_success "Limpieza completada"
}

# Mostrar logs
show_logs() {
    print_info "Mostrando logs del contenedor..."
    docker-compose logs -f credit-agent
}

# Mostrar ayuda
show_help() {
    echo "Plataforma de Créditos IA - Script de Docker"
    echo ""
    echo "Uso: $0 [comando]"
    echo ""
    echo "Comandos disponibles:"
    echo "  build      Construir imagen Docker"
    echo "  run        Ejecutar evaluación con datos de prueba"
    echo "  test       Ejecutar evaluación con datos de prueba (igual que run)"
    echo "  interactive Ejecutar contenedor en modo interactivo"
    echo "  logs       Mostrar logs del contenedor"
    echo "  clean      Limpiar contenedores e imágenes"
    echo "  help       Mostrar esta ayuda"
    echo ""
    echo "Ejemplos:"
    echo "  $0 build"
    echo "  $0 run"
    echo "  $0 test"
    echo "  $0 interactive"
}

# Función principal
main() {
    local command="${1:-help}"

    case $command in
        build)
            check_docker
            build_image
            ;;
        run|test)
            check_docker
            check_files
            run_container "python main.py test_data.json"
            ;;
        interactive)
            check_docker
            check_files
            run_interactive
            ;;
        logs)
            check_docker
            show_logs
            ;;
        clean)
            check_docker
            clean_docker
            ;;
        help|--help|-h)
            show_help
            ;;
        *)
            print_error "Comando desconocido: $command"
            echo ""
            show_help
            exit 1
            ;;
    esac
}

# Ejecutar función principal
main "$@"