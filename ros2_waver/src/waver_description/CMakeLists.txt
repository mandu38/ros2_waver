cmake_minimum_required(VERSION 3.8)
project(waver_description)

find_package(ament_cmake REQUIRED)

install(
  DIRECTORY launch urdf meshes worlds config
  DESTINATION share/${PROJECT_NAME}
)

ament_package()
