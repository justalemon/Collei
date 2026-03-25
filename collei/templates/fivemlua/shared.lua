function IsDebugEnabled()
    return GetConvarInt(GetCurrentResourceName() .. "_debug", 0) ~= 0 or GetConvarInt("lemon_debug", 0) ~= 0
end

function Debug(...)
    if IsDebugEnabled() then
        print(...)
    end
end
