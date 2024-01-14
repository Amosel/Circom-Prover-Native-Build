###

#Build targets
host:
	rm -rf build && mkdir build && cd build && \
	cmake .. -DCMAKE_BUILD_TYPE=Release -DCMAKE_INSTALL_PREFIX=../package && \
	make -j$(nproc) -vvv && make install

android:
	rm -rf build_android && mkdir build_android && cd build_android && \
	cmake .. -DTARGET_PLATFORM=ANDROID -DCMAKE_BUILD_TYPE=Release -DCMAKE_INSTALL_PREFIX=../package_android && \
	make -j$(nproc) -vvv && make install

android_x86_64:
	rm -rf build_android_x86_64 && mkdir build_android_x86_64 && cd build_android_x86_64 && \
	cmake .. -DTARGET_PLATFORM=ANDROID_x86_64 -DCMAKE_BUILD_TYPE=Release -DCMAKE_INSTALL_PREFIX=../package_android_x86_64 && \
	make -j$(nproc) -vvv && make install

ios:
	rm -rf build_ios && mkdir build_ios && cd build_ios && \
	cmake .. -GXcode -DTARGET_PLATFORM=IOS -DCMAKE_BUILD_TYPE=Release -DCMAKE_INSTALL_PREFIX=../package_ios && \
    echo "" && echo "Now open Xcode and compile the generated project" && echo ""
	
ios_simulator:
 	rm -rf build_ios_sim && mkdir build_ios_sim && cd build_ios_sim && \
 	cmake .. -GXcode -DTARGET_PLATFORM=IOS_SIMULATOR -DCMAKE_BUILD_TYPE=Release -DCMAKE_INSTALL_PREFIX=../package_ios_simulator && \
     echo "" && echo "Now open Xcode and compile the generated project" && echo ""

clean:
	rm -rf build_android build_android_x86_64 build_ios build_ios_sim package package_android \
		package_android_x86_64 package_ios package_ios_simulator depends/gmp/package depends/gmp/package_android_arm64 \
		depends/gmp/package_android_x86_64 depends/gmp/package_ios_arm64 depends/gmp/package_ios_x86_64 depends/gmp/package_ios_simulator
